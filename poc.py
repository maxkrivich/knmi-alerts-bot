import xmltodict


from icecream import ic


def read_file(file_path) -> dict:
    with open(file_path, "r") as fd:
        result = xmltodict.parse(fd.read())

        return result["report"]

    return None


def parse_report(report: dict):
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
            # 'phenonema': [ {p['phenomenon_id']: {}} for p in item['phenonema']]
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


def main():
    report = read_file("./test_file.xml")
    # breakpoint()

    result = parse_report(report)

    ic(result)


if __name__ == "__main__":
    main()
