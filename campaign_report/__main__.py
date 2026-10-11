"""Run the pipeline:   python -m campaign_report"""
from campaign_report.load import load_all, profile


def main() -> None:
    raw = load_all()
    for name, df in raw.items():
        print(profile(name, df))
        print()

    # Each day you'll add the next step of the pipeline below.


if __name__ == "__main__":
    main()