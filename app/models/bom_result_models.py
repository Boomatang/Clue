import statistics
from datetime import datetime

from app import db
from app.models import uuid_key
from app.utils import logger, isInt


class BomResult(db.Model):
    __tablename__ = "bom_result"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    __job_number = db.Column(db.String(20))
    comment = db.Column(db.String(250))
    file_id = db.Column(db.Integer, db.ForeignKey("bom_files.id"), nullable=False)
    material = db.relationship(
        "BomResultMaterial", cascade="all, delete-orphan", backref="result", lazy=True
    )
    asset = db.Column(db.String(64), index=True, default=uuid_key)
    company = db.Column(db.Integer)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    @property
    def job_number(self):
        return self.__job_number

    @job_number.setter
    def job_number(self, number):
        self.__job_number = number

    @job_number.getter
    def job_number(self):
        if self.__job_number is not None:
            return self.__job_number
        else:
            return "Unknown"

    @property
    def lengths(self):
        out = []

        for material in self.material:
            for beam in material.beams:
                if beam.length not in out:
                    out.append(beam.length)
        return out

    def timestamp_format(self):
        return f"{self.timestamp:%d/%m/%Y}"

    def delete(self):
        for material in self.material:
            material.delete()

        db.session.delete(self)
        # db.session.commit()

    def material_review(self):

        return (i.size for i in self.material)

    def required_lengths(self, size):
        lengths = []
        for item in self.material:
            if item.size == size:
                for beam in item.beams:
                    if beam.length not in lengths:
                        lengths.append(beam.length)
        return lengths

    def required_length_qty(self, size, length):
        counter = 0
        for item in self.material:
            if item.size == size:
                for beam in item.beams:
                    if beam.length == length:
                        counter = counter + beam.qty
        return counter

    def generate_results_table(self):
        logger.info("Entered the method creating the results table")
        lengths = []
        output = {}
        for material in self.material:
            for beam in material.beams:
                if beam.length not in lengths:
                    lengths.append(beam.length)

        lengths.sort()
        logger.debug(lengths)

        for material in self.material:
            output.setdefault(material.size, [])

        logger.debug(output)

        answer = {}
        for material in self.material:
            answer.setdefault(material.size, {})
            for length in lengths:
                answer[material.size][length] = 0

            for beam in material.beams:
                if beam.length in answer[material.size].keys():
                    answer[material.size][beam.length] += beam.qty

            logger.debug(answer[material.size])
        logger.debug(answer)

        output = {}

        for key in answer.keys():
            current = answer[key]
            output[key] = []

            for length in lengths:
                qty = ""
                warning = ""
                if current[length] > 0:
                    qty = current[length]
                    warning = "warning"

                output[key].append((qty, warning, length))

        logger.debug(output)

        self.result_table = output
        logger.info("Exiting the method creating the results table")

    def get_material_results(self, material):
        return self.result_table[material]

    def material_missing(self, material):
        for item in self.material:
            if material == item.size:
                return len(item.missing)

    def get_beams_for_material(self, material):

        size = BomResultMaterial.query.filter_by(
            result_id=self.id, size=material
        ).first()

        return size.beams

    def get_missing_parts_for_material(self, material):

        size = BomResultMaterial.query.filter_by(
            result_id=self.id, size=material
        ).first()

        return size.missing

    def is_missing_parts_for_material(self, material):

        size = BomResultMaterial.query.filter_by(
            result_id=self.id, size=material
        ).first()
        if len(size.missing):
            return True

        return False

    def has_missing_parts(self):
        for item in self.material:
            if len(item.missing):
                return True

        return False

    def material_average_percentage(self, material):
        size = BomResultMaterial.query.filter_by(
            result_id=self.id, size=material
        ).first()

        return size.average()

    def material_low_percentage(self, material):
        size = BomResultMaterial.query.filter_by(
            result_id=self.id, size=material
        ).first()

        return size.low()

    def material_high_percentage(self, material):
        size = BomResultMaterial.query.filter_by(
            result_id=self.id, size=material
        ).first()

        return size.high()


class BomResultMaterial(db.Model):
    __tablename__ = "bom_result_material"
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64))
    beams = db.relationship("BomResultBeam", backref="material", lazy=True)
    missing = db.relationship(
        "BomResultMissingPart",
        cascade="all,delete-orphan",
        backref="material",
        lazy=True,
    )
    result_id = db.Column(db.Integer, db.ForeignKey("bom_result.id"), nullable=False)

    def delete(self):
        for beam in self.beams:
            beam.delete()

        for part in self.missing:
            part.delete()

        db.session.delete(self)
        # db.session.commit()

    def average(self):
        return round(statistics.mean(self._all_lengths()))

    def low(self):

        return min([x for x in self._all_lengths()])

    def high(self):
        return max([x for x in self._all_lengths()])

    def _all_lengths(self):
        avg = []
        for beam in self.beams:
            avg.append(beam.get_percentage())
        if len(avg) > 0:
            return avg
        else:
            return [0, 0]


class BomResultBeam(db.Model):
    __tablename__ = "bom_result_beam"
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer)
    length = db.Column(db.Integer)
    waste = db.Column(db.Integer)
    material_id = db.Column(
        db.Integer, db.ForeignKey("bom_result_material.id"), nullable=False
    )
    parts = db.relationship(
        "BomResultBeamPart", cascade="all, delete-orphan", backref="beam", lazy=True
    )

    @property
    def usage(self):
        return self.length - self.waste

    def delete(self):
        for part in self.parts:
            part.delete()

        db.session.delete(self)
        # db.session.commit()

    def get_percentage(self):
        one = self.length / 100
        total = self.length - self.waste
        try:
            return round(total / one)
        except ZeroDivisionError:
            return 0

    def progress_bar_state(self):
        if self.get_percentage() < 60:
            return "error"
        elif self.get_percentage() < 80:
            return "warning"
        else:
            return "success"


class BomResultBeamPart(db.Model):
    __tablename__ = "bom_result_beam_part"
    id = db.Column(db.Integer, primary_key=True)
    item_no = db.Column(db.String(64))
    length = db.Column(db.Float)
    qty = db.Column(db.Integer)
    beam_id = db.Column(db.Integer, db.ForeignKey("bom_result_beam.id"), nullable=False)

    def delete(self):
        db.session.delete(self)
        # db.session.commit()


class BomResultMissingPart(db.Model):
    __tablename__ = "bom_result_missing_part"
    id = db.Column(db.Integer, primary_key=True)
    item_no = db.Column(db.String(64))
    length = db.Column(db.Float)
    qty = db.Column(db.Integer)
    material_id = db.Column(
        db.Integer, db.ForeignKey("bom_result_material.id"), nullable=False
    )

    def delete(self):
        db.session.delete(self)
        # db.session.commit()
