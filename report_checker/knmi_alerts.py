import collections
import datetime
import io
import pathlib

import xmltodict

# import copy


# from icecream import ic


def read_file(file_path: str) -> dict:
    """Reads a file and returns the content as a dictionary

    Args:
        file_path (str): Path to the file

    Returns:
        dict: Returns the content of the file as a dictionary
    """
    assert pathlib.Path(file_path).exists(), f"File {file_path} does not exist"

    with open(file_path, "r") as fd:
        result = xmltodict.parse(fd.read())

        return result["report"]

    return None


def file_to_bytesio(filepath):
    with open(filepath, "rb") as file:
        bytes_io = io.BytesIO(file.read())
    return bytes_io


def read_in_memory_file(file: io.BytesIO) -> dict:
    """Reads a file from memory and returns the content as a dictionary

    Args:
        file (io.BytesIO): File in memory

    Returns:
        dict: Returns the content of the file as a dictionary
    """

    result = xmltodict.parse(file.read())

    return result["report"]


def parse_report(report: dict) -> dict:
    """Parses the report and returns a dictionary with the metadata and forecast

    Args:
        report (dict): Report as a dictionary

    Returns:
        dict: Returns a dictionary with the metadata and forecast
    """
    report_metadata = report["metadata"]["report_structure"]

    phenonema = {
        item["phenomenon_id"]: {"phenomenon_name": item["report_phenomenon_descr"]["text"]["text_header"]}
        for item in report_metadata["report_phenomena"]["report_phenomenon"]
    }
    criteria = {
        item["criterion_id"]: {"color": item["color_id"], "description": item["criterion_descr"]}
        for item in report_metadata["report_criteria"]["report_criterion"]
    }
    locations = {
        item["location_id"]: item["location_descr"]["text"]["text_header"]
        for item in report_metadata["report_locations"]["report_location"]
    }

    # every 2 hours we get a report that contains 48 elements where it shows the condition of the weather
    forecast = [
        {
            "timeslice": item["timeslice_id"],
            "phenonema": {
                p["phenomenon_id"]: [
                    {
                        "criterion": location_report["criterion_id"],
                        "location": location_report["location_id"],
                        "text": location_report["text"],
                    }
                    for location_report in p["location"]
                ]
                for p in item["phenomenon"]
            },
        }
        for item in report["data"]["cube"]["timeslice"]
    ]

    return {
        "metadata": {
            "locations": locations,
            "criteria": criteria,
            "phenomena": phenonema,
        },
        "forecast": forecast,
    }


def detect_alerts(report: dict) -> dict:
    """Detects alerts in the report for each location

    Args:
        report (dict): Report as a dictionary

    Returns:
        dict: Returns a dictionary with the alerts for each location
    """
    result = {}

    locations = report["metadata"]["locations"]
    # ic(len(locations))

    for location in locations:
        result[location] = {phenonema: list() for phenonema in report["metadata"]["phenomena"]}

    green_criteria = [
        code for (code, criteria) in report["metadata"]["criteria"].items() if criteria["color"].lower() == "green"
    ]

    for forecast in report["forecast"]:
        for phenonema in forecast["phenonema"].keys():
            for location in forecast["phenonema"][phenonema]:
                if location["criterion"] not in green_criteria:
                    text = {}
                    for txt in location["text"]:
                        text[txt["text_language_id"]] = txt["text_data"]

                    result[location["location"]][phenonema].append(
                        {
                            "time": datetime.datetime.fromisoformat(forecast["timeslice"]),
                            "criterion": location["criterion"],
                            "text": text,
                        }
                    )

    return result


def squash_alerts(alerts: dict) -> dict:
    """Squashes the alerts to get the start and end time of the alert. Specifies time range of the alert

    Args:
        alerts (dict): Alerts for each location

    Returns:
        dict: Returns a dictionary with the start and end time of the alert
    """
    result = collections.defaultdict(dict)
    for location, phenonemas in alerts.items():
        for phenonema, alerts in phenonemas.items():
            if len(alerts) > 0:
                result[location][phenonema] = {
                    "start_time": alerts[0]["time"],
                    "end_time": alerts[-1]["time"],
                    "text": alerts[-1]["text"],
                    "criteria": alerts[-1]["criterion"],
                }

    return dict(result)


def enrich_alert(report_metadata: dict, alerts: dict) -> dict:
    """Enriches the alerts with the metadata of the report

    Args:
        report_metadata (dict): Report metadata
        alerts (dict): alerts

    Returns:
        dict: Returns a dictionary with the enriched alerts
    """
    result = {location: list() for location in report_metadata["locations"].values()}

    for location, phenonemas in alerts.items():
        result[report_metadata["locations"][location]] = []

        for phenonema, alert in phenonemas.items():
            result[report_metadata["locations"][location]].append(
                {
                    "phenomenon_name": report_metadata["phenomena"][phenonema]["phenomenon_name"],
                    "code": report_metadata["criteria"][alert["criteria"]]["color"],
                    "start_time": alert["start_time"],
                    "end_time": alert["end_time"],
                    "text": alert["text"],
                }
            )

    return result


def get_alerts(report_file: io.BytesIO) -> dict:
    """Get the alerts from the report

    Args:
        report_file (io.BytesIO): Report file

    Returns:
        dict: Returns the alerts from the report
    """

    # report = read_file("./test_file.xml")
    # file = file_to_bytesio("./test_file.xml")

    assert report_file, "Report file is empty"

    report = read_in_memory_file(report_file)
    parsed_report = parse_report(report)
    alerts = detect_alerts(parsed_report)
    alerts = squash_alerts(alerts)
    final_alerts = enrich_alert(parsed_report["metadata"], alerts)

    return final_alerts


def main():
    pass


if __name__ == "__main__":
    main()


__all__ = ["get_alerts"]
