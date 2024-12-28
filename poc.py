import xmltodict
import datetime
import collections
# import copy


from icecream import ic


def read_file(file_path) -> dict:
    with open(file_path, "r") as fd:
        result = xmltodict.parse(fd.read())

        return result["report"]

    return None


def parse_report(report: dict) -> dict:
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


def enrich_alert(report_metadata: dict, alerts: dict):
    result = {
        location: list()
        for location in report_metadata["locations"].values()
    }

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


def main():
    report = read_file("./test_file.xml")

    result = parse_report(report)

    alerts = detect_alerts(result)

    alerts = squash_alerts(alerts)

    final_alerts = enrich_alert(result["metadata"], alerts)

    # final_report = analyse_alerts(result['metadata'], alerts)

    ic(final_alerts)


if __name__ == "__main__":
    main()
