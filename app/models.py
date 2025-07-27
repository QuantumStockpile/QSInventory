from tortoise import fields, validators

from ms_core import AbstractModel


class ExtendedAbstractModel(AbstractModel):
    updated_at = fields.DatetimeField(auto_now=True)


class Equipment(ExtendedAbstractModel):
    name = fields.CharField(max_length=255)
    serial_number = fields.CharField(max_length=255)
    status = fields.CharField(max_length=50)
    condition = fields.IntField(
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(10)]
    )
    photo_url = fields.CharField(max_length=500, null=True)
    qr_code_data = fields.CharField(max_length=500, null=True)
    metadata = fields.JSONField(null=True)

    type: fields.ForeignKeyRelation["EquipmentType"] = fields.ForeignKeyField(
        "models.EquipmentType", "equipments"
    )

    location: fields.ForeignKeyRelation["Location"] = fields.ForeignKeyField(
        "models.Location", "equipments"
    )

    history: fields.ReverseRelation["EquipmentHistoryEntry"]

    class Meta:  # type: ignore
        table = "equipments"


class EquipmentType(ExtendedAbstractModel):
    name = fields.CharField(max_length=255)

    equipments: fields.ReverseRelation[Equipment]

    class Meta:  # type: ignore
        table = "equipment_types"


class Location(ExtendedAbstractModel):
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=500, null=True)

    equipments: fields.ReverseRelation[Equipment]

    class Meta:  # type: ignore
        table = "locations"


class EquipmentHistoryEntry(ExtendedAbstractModel):
    action = fields.CharField(max_length=10)
    old = fields.JSONField(null=True)
    new = fields.JSONField(null=True)

    email = fields.CharField(256)

    equipment: fields.ForeignKeyRelation[Equipment] = fields.ForeignKeyField(
        "models.Equipment", "history"
    )

    class Meta:  # type: ignore
        table = "history"
