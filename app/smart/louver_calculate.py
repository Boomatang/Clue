import math


class MeshCalculator:
    def __init__(self, width, height, mesh_efficiency):
        self.width = width
        self.height = height
        self.mesh_efficiency = mesh_efficiency
        self.mesh_frame_height_allowance = 46

    @property
    def mesh_frame_width_allowance(self):
        if self.width < 1000:
            return 46
        else:
            return 96

    @property
    def total_unit_area(self):
        return self.height * self.width

    @property
    def frame_area(self):
        return (self.width - self.mesh_frame_width_allowance) * (self.height - self.mesh_frame_height_allowance)

    @property
    def unit_efficiency(self):
        return (self.mesh_efficiency * self.frame_area) / self.total_unit_area

    @property
    def free_area_of_mesh(self):
        return self.unit_efficiency


class LouverCalculator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.frame_height_allowance = 144
        self.standard_blade_gap = 28

    @property
    def frame_width_allowance(self):
        if self.width < 1000:
            return 60
        else:
            return 120

    @property
    def total_unit_area(self):
        return self.height * self.width

    @property
    def number_of_blade_gaps(self):
        return (self.height - self.frame_height_allowance)/45

    @property
    def number_of_full_blade_gaps(self):
        return math.floor(self.number_of_blade_gaps)

    @property
    def ratio_of_partial_blade_gap(self):
        return self.number_of_blade_gaps - self.number_of_full_blade_gaps

    @property
    def height_of_remaining_partial_blade_gap(self):
        return 28 * self.ratio_of_partial_blade_gap

    @property
    def effective_partial_blade_gap(self):
        if self.height_of_remaining_partial_blade_gap < 16:
            return self.height_of_remaining_partial_blade_gap
        else:
            return 16

    @property
    def louver_free_area(self):
        return self.width * ((self.number_of_full_blade_gaps * self.standard_blade_gap)
                             + self.effective_partial_blade_gap)

    @property
    def free_area_of_louver_unit(self):
        return self.louver_free_area / self.total_unit_area


def calculate_louver_efficiency(louver_width, louver_height, mesh_efficiency):
    mesh = MeshCalculator(louver_width, louver_height, mesh_efficiency)
    louver = LouverCalculator(louver_width, louver_height)

    if mesh.free_area_of_mesh < louver.free_area_of_louver_unit:
        return mesh.free_area_of_mesh
    else:
        return louver.free_area_of_louver_unit


def louver_efficiency(louver_width, louver_height, mesh_efficiency):

    output = calculate_louver_efficiency(louver_width, louver_height, mesh_efficiency)
    output = str(round(output * 100, 1))

    return output + '%'


if __name__ == "__main__":
    sample_mesh = MeshCalculator(900, 300, .3)
    print(sample_mesh.free_area_of_mesh)

    sample_louver = LouverCalculator(900, 300)
    print(sample_louver.free_area_of_louver_unit)

    print(round(calculate_louver_efficiency(900, 300, .3), 2))

    print(louver_efficiency(900, 300, .7))
