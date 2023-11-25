import xml.etree.ElementTree as ET
import json


def float_perc(value: str | float) -> float:
    """Converts a string to a float as %."""
    return round(float(value) * 100)


def seconds_to_minutes(seconds: int) -> tuple[int, int]:
    """Converts seconds to minutes."""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return minutes, remaining_seconds


class WorkoutSegment:
    """Represents a segment of a workout.

    Example:
    z = ZwoParser("../demo.zwo")
    z.parse()

    z.workout_segments # List of WorkoutSegment objects
    """

    def __init__(
        self,
        start_time: int,
        duration: tuple[int, int],
        segment_type: str,
        power: tuple[int, int],
        cadence: int,
        text_events: list[str] = [],
    ):
        self.start_time = start_time
        self.duration = duration
        self.segment_type = segment_type
        self.power = power
        self.cadence = cadence
        self.text_events = text_events

    def get_time_string(self):
        return f", {self.duration[1]} seconds" if self.duration[1] > 0 else ""

    def get_power_string(self):
        if self.power[0] != 0 and self.power[1] != 0:
            return f"{self.power[0]} %FTP - {self.power[1]} FTP%"
        else:
            return f"{self.power[0]} %FTP"

    def get_cadence_string(self):
        if self.cadence == 0:
            return "Any"
        else:
            return f"{self.cadence} RPM"

    def __repr__(self):
        return f"{self.segment_type}. Duration = {self.duration[0]} minutes{self.get_time_string()}. Power = {self.get_power_string()}, Cadence={self.get_cadence_string()}"


class ZwoParser:
    """Parses a Zwift Workout XML file."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.workout_segments = []

    def parse(self):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        workout = root.find("workout")

        time = 0
        for node in workout:
            duration = int(node.get("Duration", 0))
            power = (
                float_perc(node.get("Power", 0)),
                float_perc(node.get("PowerHigh", 0)),
            )
            cadence = int(node.get("Cadence", 0))
            text_events = self.parse_text_events(node)
            segment = WorkoutSegment(
                time,
                seconds_to_minutes(duration),
                node.tag.lower(),
                power,
                cadence,
                text_events,
            )
            self.workout_segments.append(segment)
            time += duration

    def parse_text_events(self, node):
        return [
            (int(te.get("timeoffset")), te.get("message"))
            for te in node.iter("textevent")
        ]


def output_workout(segments, output_type="txt"):
    if output_type == "json":
        return json.dumps([seg.__dict__ for seg in segments], indent=4)
    elif output_type == "txt":
        return "\n".join(str(seg) for seg in segments)
