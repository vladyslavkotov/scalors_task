from Validator import Validator
from GroupedPositions import GroupedPositions

grouped_positions = GroupedPositions.create("Test.xlsx")

v = Validator(grouped_positions)