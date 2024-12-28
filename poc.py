import xmltodict


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
            'phenonema': {
                p["phenomenon_id"]: [
                    {
                        "criterion": location_report["criterion_id"],
                        "location": location_report["location_id"],
                        "text": location_report["text"]
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


    for location in locations:
        result[location] =  { phenonema: list() for phenonema in report["metadata"]["phenomena"]}

    green_criteria = [
        code
        for (code, criteria) in report["metadata"]["criteria"].items()
        if criteria["color"].lower() == "green"
    ]

    for forecast in report["forecast"]:
        for phenonema in forecast["phenonema"].keys():
            for location in forecast["phenonema"][phenonema]:
                if location["criterion"] not in green_criteria:
                    result[location["location"]][phenonema].append(
                        {
                            "time": forecast["timeslice"],
                            "criterion": location["criterion"],
                            "text": location["text"]
                        }
                    )


    return result


def main():
    report = read_file("./test_file.xml")

    result = parse_report(report)

    alerts = detect_alerts(result)

    ic(alerts['NH'])


if __name__ == "__main__":
    main()
