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





















class User(db.Model):

    __tablename__='users'

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    company_name = db.Column(db.String(50), nullable=True)
    contact_name = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.String(50), nullable=True)

    paid_until = db.Column(db.DateTime(), default=datetime.utcnow)
    
    ein_no = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(256), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    usa_state = db.Column(db.Enum(USAState), default=USAState.FL)
    zipcode = db.Column(db.String(50), nullable=True)
    fax = db.Column(db.String(50), nullable=True)

    is_active = db.Column(db.Boolean(), default=False)

    trucks = db.relationship("Truck", backref='owner', lazy=True)
    drivers = db.relationship("Driver", backref='company', lazy=True)
    
    payments = db.relationship("Payment", backref='owner', lazy=True)

    last_token_password = db.Column(db.String(256), default="-1")


    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def __str__(self):
        return str(self.id) + " - " + str(self.email)

    def __repr__(self):
        return f"<User {self.email} - {self.company_name}>"







class Driver(db.Model):

    __tablename__='drivers'

    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    usa_state = db.Column(db.Enum(USAState), default=USAState.FL)
    cdl_no = db.Column(db.String(50), default=False)
    email = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)

    user = db.Column(db.Integer(), db.ForeignKey("users.id"))
    truck = db.relationship("Truck", uselist=False, backref="driver")

    last_token_password = db.Column(db.String(256), default="-1")


    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def __str__(self):
        return str(self.id) + " - " + str(self.email)

    def __repr__(self):
        return f"<Driver {self.id} - {self.email}>"









class Truck(db.Model):

    __tablename__='trucks'

    id = db.Column(db.Integer(), primary_key=True)
    truck_unit = db.Column(db.String(50), nullable=True)
    gross_vehicle_weight = db.Column(db.String(50), nullable=False)
    fuel_type = db.Column(db.String(50), nullable=False)
    vim_no = db.Column(db.String(50), nullable=False)
    fleet_name = db.Column(db.String(50), nullable=True)
    vehicle_fleet_no = db.Column(db.String(50), nullable=True)
    truck_make = db.Column(db.String(50), nullable=False)
    truck_model = db.Column(db.String(50), nullable=False)
    license_plate_no = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(50), nullable=False)
    unloaded_vehicle_weight = db.Column(db.String(50), nullable=False)
    axle = db.Column(db.String(50), nullable=False)
    ny_hut = db.Column(db.String(50), nullable=True)
    or_plate_pass = db.Column(db.String(50), nullable=True)

    user = db.Column(db.Integer(), db.ForeignKey("users.id"))
    current_driver = db.Column(db.Integer(), db.ForeignKey("drivers.id"))

    new_entries = db.relationship("NewEntry", backref='current_truck', lazy=True)
    quarters = db.relationship("Quarter", backref='current_truck', lazy=True)
    



    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def __str__(self):
        return str(self.id) + " - " + str(self.license_plate_no)

    def __repr__(self):
        return f"<Truck {self.id} - {self.license_plate_no}>"










class Payment(db.Model):

    __tablename__='payments'

    id = db.Column(db.Integer(), primary_key=True)
    amount = db.Column(db.Float(), default=0.0)
    charge_id = db.Column(db.String(256), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.Column(db.Integer(), db.ForeignKey("users.id"))
    



    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def __str__(self):
        return str(self.id) + " - " + str(self.created)

    def __repr__(self):
        return f"<Truck {self.id} - {self.created}>"