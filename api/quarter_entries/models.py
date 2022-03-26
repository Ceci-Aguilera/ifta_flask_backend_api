from config import db
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import backref


class USAState(Enum):
    AL="AL"
    AK="AK"
    AZ="AZ"
    AR="AR"
    CA="CA"
    CO="CO"
    CT="CT"
    DE="DE"
    FL="FL"
    GA="GA"
    HI="HI"
    ID="ID"
    IL="IL"
    IN="IN"
    IA="IA"
    KS="KS"
    KY="KY"
    LA="LA"
    ME="ME"
    MD="MD"
    MA="MA"
    MI="MI"
    MN="MN"
    MS="MS"
    MO="MO"
    MT="MT"
    NE="NE"
    NV="NV"
    NH="NH"
    NJ="NJ"
    NM="NM"
    NY="NY"
    NC="NC"
    ND="ND"
    OH="OH"
    OK="OK"
    OR="OR"
    PA="PA"
    RI="RI"
    SC="SC"
    SD="SD"
    TN="TN"
    TX="TX"
    UT="UT"
    VT="VT"
    VA="VA"
    WA="WA"
    WV="WV"
    WI="WI"
    WY="WY"



class NewEntry(db.Model):

    __tablename__='newentries'

    id = db.Column(db.Integer(), primary_key=True)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    day = db.Column(db.Integer(), default=1)
    month = db.Column(db.Integer(), default=1)
    year = db.Column(db.Integer(), default=1)
    current_quarter = db.Column(db.Integer(), default=1)
    toll_miles = db.Column(db.Float(), default=0.0)
    non_toll_miles = db.Column(db.Float(), default=0.0)
    fuel_gallons = db.Column(db.Float(), default=0.0)
    fuel_price = db.Column(db.Float(), default=0.0)
    usa_state = db.Column(db.Enum(USAState), default=USAState.FL)
    truck = db.Column(db.Integer(), db.ForeignKey("trucks.id"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def __str__(self):
        return str(self.id) + " - " + str(self.usa_state)
    
    def __repr__(self):
        return f"<NewEntry {self.id} - {self.usa_state}>"








class StateQuarterReport(db.Model):

    ___tablename__='statequarterreports'

    id = db.Column(db.Integer(), primary_key=True)
    usa_state = db.Column(db.Enum(USAState), default=USAState.FL)
    toll_miles = db.Column(db.Float(), default=0.0)
    non_toll_miles = db.Column(db.Float(), default=0.0)
    fuel_gallons = db.Column(db.Float(), default=0.0)

    fuel_tax_owned = db.Column(db.Float(), default=0.0)

    quarter = db.Column(db.Integer(), db.ForeignKey("quarters.id"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()







class Quarter(db.Model):

    __tablename__='quarters'

    id = db.Column(db.Integer(), primary_key=True)
    number = db.Column(db.Integer(), default=1)
    year = db.Column(db.Integer(), default=2022)

    toll_miles = db.Column(db.Float(), default=0.0)
    non_toll_miles = db.Column(db.Float(), default=0.0)
    fuel_gallons = db.Column(db.Float(), default=0.0)
    mpg = db.Column(db.Float(), default=0.0)

    fuel_tax_owned = db.Column(db.Float(), default=0.0)

    truck = db.Column(db.Integer(), db.ForeignKey("trucks.id"))
    state_quarter_report = db.relationship("StateQuarterReport", backref='current_quarter', lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return str(self.id) + " - " + str(self.number) + "/" + str(self.year)
    
    def __repr__(self):
        return f"<Quarter {self.id} - {self.number} / {self.year}>"









    






class StateTax(db.Model):
    ___tablename__='statetaxes'

    id = db.Column(db.Integer(), primary_key=True)
    number = db.Column(db.Integer(), default=1)
    year = db.Column(db.Integer(), default=2022)
    usa_state = db.Column(db.Enum(USAState), default=USAState.FL)
    tax = db.Column(db.Float(), default=0.0)
    fuel = db.Column(db.String(50), default="Biodiesel")

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return str(self.id) + " - " + str(self.number) + "/" + str(self.year)
    
    def __repr__(self):
        return f"<StateTax {self.id} - {self.number} / {self.year}>"
