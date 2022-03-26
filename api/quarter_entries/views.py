from .models import *

from flask import request
from flask_restx import Resource, Namespace, fields
from http import HTTPStatus
from flask_jwt_extended import (
	create_access_token,
	create_refresh_token,
	jwt_required,
	get_jwt_identity,
	get_jwt
)

from api.user_account.models import *

def get_current_quarter(month):
	current_quarter = 1
	if month > 3:
		current_quarter = 2
	if month > 6:
		current_quarter = 3
	if month > 9:
		current_quarter = 4
	return current_quarter



quarter_taxes_namespace = Namespace(
	'manage-quarter-taxes', description="A Namespace for managing new entries")

new_entry_model = quarter_taxes_namespace.model(
	"NewEntry", {
		'id': fields.Integer(),
		'day': fields.Integer(),
		'month': fields.Integer(),
		'year': fields.Integer(),
		'toll_miles': fields.Float(),
		'non_toll_miles': fields.Float(),
		'fuel_gallons': fields.Float(),
		'fuel_price': fields.Float(),
		'usa_state': fields.String(required=True, enum=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'])
	}
)



state_report_model = quarter_taxes_namespace.model(
	"StateQuarterReport", {
		'id': fields.Integer(),
		'mpg': fields.Float(),
		'toll_miles': fields.Float(),
		'non_toll_miles': fields.Float(),
		'fuel_gallons': fields.Float(),
		'fuel_tax_owned': fields.Float(),
		'usa_state': fields.String(required=True, enum=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'])
	}
)



quarter_model = quarter_taxes_namespace.model(
	"Quarter", {
		'id': fields.Integer(),
		'number': fields.Integer(),
		'mpg': fields.Float(),
		'toll_miles': fields.Float(),
		'non_toll_miles': fields.Float(),
		'fuel_gallons': fields.Float(),
		'fuel_tax_owned': fields.Float(),
		'usa_state': fields.String(required=True, enum=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'])
	}
)





truck_info_model = quarter_taxes_namespace.model(
	"Truck", {
		"id": fields.Integer(required=True, description="An id"),
		"truck_unit": fields.String(required=True, description="A truck unit"),
		"gross_vehicle_weight": fields.String(required=True, description="A gross vehicle weight"),
		"fuel_type": fields.String(required=True, description="A fuel type"),
		"vim_no": fields.String(required=True, description="A vim number"),
		"fleet_name": fields.String(required=True, description="A fleet name"),
		"vehicle_fleet_no": fields.String(required=True, description="A vehicle fleet number"),
		"truck_make": fields.String(required=True, description="A truck make"),
		"truck_model": fields.String(required=True, description="A truck model"),
		"license_plate_no": fields.String(required=True, description="A license plate number"),
		"year": fields.String(required=True, description="A year"),
		"unloaded_vehicle_weight": fields.String(required=True, description="An unload vehicle weight"),
		"axle": fields.String(required=True, description="An axle"),
		"ny_hut": fields.String(required=True, description="A ny hut"),
		"or_plate_pass": fields.String(required=True, description="An or plate or pass"),
		'current_driver': fields.Integer(description="A current driver")
	}
)




@quarter_taxes_namespace.route("/new-entry/create")
class CreateGetAllNewEntry(Resource):

	@jwt_required(refresh=False)
	def post(self):
		"""
			Create New Entry for the Driver
		"""

		# try:
		if True:
			email = get_jwt_identity()
			
			driver = Driver.query.filter_by(email=email).first()

			current_truck = Truck.query.filter_by(current_driver=driver.id).first()

			data = request.get_json()

			month = data.get('month')
			year = data.get("year")

			current_quarter = get_current_quarter(month)

			new_entry = NewEntry(
				current_quarter = current_quarter,
				day = data.get('day'),
				month = data.get('month'),
				year = data.get("year"),
				toll_miles = data.get('toll_miles'),
				non_toll_miles = data.get('non_toll_miles'),
				fuel_gallons = data.get('fuel_gallons'),
				fuel_price = data.get('fuel_price'),
				usa_state = data.get('usa_state'),
				truck = current_truck.id
			)

			new_entry.save()

			quarter = Quarter.query.filter_by(number=current_quarter, year=year, truck=current_truck.id).first()
			if not quarter:
				quarter = Quarter(number=current_quarter, year=year, truck=current_truck.id)
				quarter.save()

			quarter.toll_miles = quarter.toll_miles + new_entry.toll_miles
			quarter.non_toll_miles = quarter.non_toll_miles + new_entry.non_toll_miles
			quarter.fuel_gallons = quarter.fuel_gallons + new_entry.fuel_gallons

			quarter.update()


			quarter_state_report = StateQuarterReport.query.filter_by(quarter=quarter.id, usa_state=new_entry.usa_state).first()
			if not quarter_state_report:
				quarter_state_report = StateQuarterReport(quarter=quarter.id, usa_state=new_entry.usa_state)
				quarter_state_report.save()

			quarter_state_report.toll_miles = quarter_state_report.toll_miles + new_entry.toll_miles
			quarter_state_report.non_toll_miles = quarter_state_report.non_toll_miles + new_entry.non_toll_miles
			quarter_state_report.fuel_gallons = quarter_state_report.fuel_gallons + new_entry.fuel_gallons

			quarter_state_report.update()



			return "Success", HTTPStatus.CREATED
			
		# except:
		else:
			return "Error", HTTPStatus.BAD_REQUEST


@quarter_taxes_namespace.route("/new-entry/list")
class CreateGetAllNewEntry(Resource):
	@jwt_required(refresh=False)
	@quarter_taxes_namespace.marshal_with(new_entry_model, as_list=True)
	def post(self):
		"""
			List all of the Entries of the Driver (for current quarter)
		"""

		email = get_jwt_identity()
			
		driver = Driver.query.filter_by(email=email).first()

		current_truck = Truck.query.filter_by(current_driver=driver.id).first()
		
		data = request.get_json()

		month = data.get('month')
		year = data.get("year")

		current_quarter = get_current_quarter(month)


		try:
			new_entries = NewEntry.query.filter_by(current_quarter=current_quarter, year = year, truck = current_truck.id)
			return new_entries.all(), HTTPStatus.OK 
		except:
			return "Error", HTTPStatus.BAD_REQUEST

		







@quarter_taxes_namespace.route("/new-entry/delete/<id>")
class CreateGetAllNewEntry(Resource):
	@jwt_required(refresh=False)
	def delete(self, id):
		"""
			Delete New Entry by id
		"""

		email = get_jwt_identity()
			
		driver = Driver.query.filter_by(email=email).first()

		current_truck = Truck.query.filter_by(current_driver=driver.id).first()
		
		
		try:
			new_entry = NewEntry.query.filter_by(id=id, truck = current_truck.id).first()

			quarter = Quarter.query.filter_by(year=new_entry.year, number=new_entry.current_quarter, truck=current_truck.id).first()

			quarter.toll_miles = quarter.toll_miles - new_entry.toll_miles
			quarter.non_toll_miles = quarter.non_toll_miles - new_entry.non_toll_miles
			quarter.fuel_gallons = quarter.fuel_gallons - new_entry.fuel_gallons

			quarter.update()


			quarter_state_report = StateQuarterReport.query.filter_by(quarter=quarter.id, usa_state=new_entry.usa_state).first()
			quarter_state_report.toll_miles = quarter_state_report.toll_miles - new_entry.toll_miles
			quarter_state_report.non_toll_miles = quarter_state_report.non_toll_miles - new_entry.non_toll_miles
			quarter_state_report.fuel_gallons = quarter_state_report.fuel_gallons - new_entry.fuel_gallons

			quarter_state_report.update()




			new_entry.delete()
		
			return "Success", HTTPStatus.OK 
		except:
			return "Error", HTTPStatus.BAD_REQUEST







@quarter_taxes_namespace.route("/calculate-taxes/<year>/<month>/<number>")
class CalculateTaxes(Resource):

	@jwt_required(refresh=False)
	@quarter_taxes_namespace.marshal_with(quarter_model)
	@quarter_taxes_namespace.marshal_with(state_report_model, as_list=True)
	def get(self, year, month, number):
		email = get_jwt_identity()
			
		driver = Driver.query.filter_by(email=email).first()

		current_truck = driver.current_truck

		# data = request.get_json()

		# current_month = data.get('month')
		# current_year = data.get("year")

		if month != 0:
			current_quarter = get_current_quarter(month)
		else:
			current_quarter = number

		quarter = Quarter.query.filter_by(number=current_quarter, year=year, truck=current_truck.id)

		mpg = quarter.toll_miles / quarter.fuel_gallons
		quarter.mpg = round(mpg,2)

		state_reports = StateQuarterReport.query.filte_by(quarter=quarter)

		for state_report in state_reports:
			tax_gallons = state_report.toll_miles / mpg
			state_tax = StateTax.query.filter_by(usa_state = state_report.usa_state, number = current_quarter, year=year)
			net_tax_gallons = tax_gallons - state_report.fuel_gallons
			state_report.fuel_tax_owned = net_tax_gallons * state_tax.tax
			state_report.update()
			quarter_fuel_tax_owned = quarter_fuel_tax_owned + state_report.fuel_tax_owned

		quarter.fuel_tax_owned = quarter_fuel_tax_owned
		quarter.update()

		return{"Quarter": quarter, "State_Reports": state_reports}, HTTPStatus.OK


@quarter_taxes_namespace.route("/taxes-truck-year")
class AllTaxesPerYear(Resource):

	@jwt_required(refresh=False)
	def get(self):

		email = get_jwt_identity()

		driver = Driver.query.filter_by(email=email).first()

		current_truck = driver.current_truck


		tax_years = [year in Quarter.query.filter_by(truck=current_truck.id).values("year").distinct()]

		return tax_years, HTTPStatus.OK



@quarter_taxes_namespace.route("/all-year-taxes/<year>")
class AllYearTaxes(Resource):

	@jwt_required(refresh=False)
	def get(self, year):

		email = get_jwt_identity()
		
		driver = Driver.query.filter_by(email=email).first()

		current_truck = driver.current_truck


		tax_years = [number in Quarter.query.filter_by(truck=current_truck.id, year=year).values("number").distinct()]

		return tax_years, HTTPStatus.OK





@quarter_taxes_namespace.route("/send-taxes/<year>/<month>/<number>")
class SendTruckTaxes(Resource):

	@jwt_required(refresh=False)
	def get(self, year, month, number):
		email = get_jwt_identity()
			
		driver = Driver.query.filter_by(email=email).first()

		current_truck = driver.current_truck

		if month != 0:
			current_quarter = get_current_quarter(month)
		else:
			current_quarter = number

		quarter = Quarter.query.filter_by(number=current_quarter, year=year, truck=current_truck.id)
		state_reports = StateQuarterReport.query.filter_by(quarter=quarter)











@quarter_taxes_namespace.route("/taxes-truck-year/<year>")
class TaxesTruckYear(Resource):

	@jwt_required(refresh=False)
	@quarter_taxes_namespace.marshal_with(truck_info_model)
	def get(self, year):

		email = get_jwt_identity()
		
		user = User.query.filter_by(email=email).first()

		all_trucks = Truck.query.filter_by(user=user.id).join(Quarter).filter(Quarter.year==year).all()

		return all_trucks, HTTPStatus.OK



@quarter_taxes_namespace.route("/taxes-report/<year>/<truck_id>")
class TaxesOfOneYear(Resource):

	@jwt_required(refresh=False)
	@quarter_taxes_namespace.marshal_with(quarter_model, as_list=True)
	def get(self, year, truck_id):

		email = get_jwt_identity()
		
		user = User.query.filter_by(email=email).first()

		truck = Truck.query.filter_by(id=truck_id, user=user.id).first()

		quarters = Quarter.query.filter_by(truck=truck.id, year=year).all()

		return quarters, HTTPStatus.OK



@quarter_taxes_namespace.route("/taxes-report/<year>/<truck_id>/<quarter_number>")
class CalculateTaxesOneYear(Resource):

	@jwt_required(refresh=False)
	@quarter_taxes_namespace.marshal_with(quarter_model)
	@quarter_taxes_namespace.marshal_with(state_report_model, as_list=True)
	def get(self, year, truck_id, quarter_number):

		email = get_jwt_identity()
		
		user = User.query.filter_by(email=email).first()

		current_truck = Truck.query.filter_by(id=truck_id, user=user.id).first()


		current_quarter = quarter_number

		quarter = Quarter.query.filter_by(number=current_quarter, year=year, truck=current_truck.id).first()

		mpg = quarter.toll_miles / quarter.fuel_gallons

		quarter.mpg = round(mpg,2)

		state_reports = StateQuarterReport.query.filter_by(quarter=quarter.id).all()

		quarter_fuel_tax_owned = 0

		for state_report in state_reports:
			tax_gallons = state_report.toll_miles / mpg
			state_tax = StateTax.query.filter_by(usa_state = state_report.usa_state, number = current_quarter, year=year).first()
			net_tax_gallons = tax_gallons - state_report.fuel_gallons
			state_report.fuel_tax_owned = net_tax_gallons * state_tax.tax
			state_report.update()
			quarter_fuel_tax_owned = quarter_fuel_tax_owned + state_report.fuel_tax_owned

		quarter.fuel_tax_owned = quarter_fuel_tax_owned
		quarter.update()

		print(quarter.mpg)

		return quarter, HTTPStatus.OK


@quarter_taxes_namespace.route("/taxes-report/states-reports/<year>/<truck_id>/<quarter_number>")
class CalculateTaxesOneYear(Resource):

	@jwt_required(refresh=False)
	@quarter_taxes_namespace.marshal_with(state_report_model, as_list=True)
	def get(self, year, truck_id, quarter_number):

		email = get_jwt_identity()
		
		user = User.query.filter_by(email=email).first()

		current_truck = Truck.query.filter_by(id=truck_id, user=user.id).first()


		current_quarter = quarter_number

		quarter = Quarter.query.filter_by(number=current_quarter, year=year, truck=current_truck.id).first()

		state_reports = StateQuarterReport.query.filter_by(quarter=quarter.id).all()

		return state_reports, HTTPStatus.OK
