import enum


class Scope(str, enum.Enum):
    SMC = 'smc'
    PRODUCT = 'product'
    APP = 'app'
    ORG = 'org'
