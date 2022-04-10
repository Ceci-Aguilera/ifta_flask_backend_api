import os
from http import HTTPStatus
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from dateutil.relativedelta import relativedelta
import base64
import secrets

import flask_mail

import os
from threading import Thread
from time import sleep



from flask import request, redirect, make_response, send_from_directory, current_app
from flask_restx import Resource,Namespace, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
	create_access_token,
	create_refresh_token,
	jwt_required,
	get_jwt_identity,
	get_jwt
)

from werkzeug.utils import secure_filename

import stripe


from .models import User, Driver, Truck, Payment
from flask import current_app, render_template
from config import db



class SimpleDateField(fields.Raw):
	def format(self, value):
		return value.strftime('%Y-%m-%d')



user_account_namespace=Namespace('user-account', description="A Namespace for user account management")

signup_model = user_account_namespace.model(
	"User", {
		'company_name': fields.String(required=True, description="A company name"),
		'contact_name': fields.String(required=True, description="A contact name"),
		'email': fields.String(required=True, description="An email"),
		'phone': fields.String(required=True, description="An phone"),
		'password': fields.String(required=True, description="A password"),
		'ein_no': fields.String(required=True, description="An ein number"),
		'address': fields.String(required=True, description="An address"),
		'city': fields.String(required=True, description="A city"),
		'zipcode': fields.String(required=True, description="A zip code"),
		'fax': fields.String(required=True, description="A fax")
	}
)

sign_up_driver_model = user_account_namespace.model(
	"Driver", {
		'first_name': fields.String(required=True, description="A first name"),
		'last_name': fields.String(required=True, description="A last name"),
		'email': fields.String(required=True, description="An email"),
		'cdl_no': fields.String(required=True, description="A cdl number"),
		'password': fields.String(required=True, description="A password")
	}
)







driver_info_model = user_account_namespace.model(
	"Driver", {
		"id": fields.Integer(required=True, description="An id"),
		'first_name': fields.String(required=True, description="A first name"),
		'last_name': fields.String(required=True, description="A last name"),
		'email': fields.String(required=True, description="An email"),
		'cdl_no': fields.String(required=True, description="A cdl number")
	}
)

login_model = user_account_namespace.model(
	"Login", {
		'email': fields.String(required=True, description="An email"),
		'password': fields.String(required=True, description="A password"),
	}
)

user_info_model = user_account_namespace.model(
	"User", {
		'company_name': fields.String(required=True, description="A company name"),
		'contact_name': fields.String(required=True, description="A contact name"),
		'email': fields.String(required=True, description="An email"),
		'paid_until': SimpleDateField(),
		'phone': fields.String(required=True, description="An phone"),
		'ein_no': fields.String(required=True, description="An ein number"),
		'address': fields.String(required=True, description="An address"),
		'city': fields.String(required=True, description="A city"),
		'zipcode': fields.String(required=True, description="A zip code"),
		'fax': fields.String(required=True, description="A fax"),
		'usa_state': fields.String(required=True, enum=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'])
	}
)

truck_info_model = user_account_namespace.model(
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






def current_quarter_end(current_time_date):

	today = current_time_date
	today_year = current_time_date.year

	if today < datetime(today_year, 4, 30):
		return datetime(today_year, 4, 30)

	elif today < datetime(today_year, 7, 31):
		return datetime(today_year, 7, 31)

	elif today < datetime(today_year, 10, 31):
		return datetime(today_year, 10, 31)

	else:
		return datetime(today_year+1, 1, 31)


def add_paid_quarters(quarters, current_time_date):
	if quarters == 1:
		return current_quarter_end(current_time_date)
	elif quarters == 2:
		current_time_date = current_time_date + relativedelta(months = 3)
		return current_quarter_end(current_time_date)
	elif quarters == 3:
		current_time_date = current_time_date + relativedelta(months = 6)
		return current_quarter_end(current_time_date)
	else:
		current_time_date = current_time_date + relativedelta(months = 9)
		return current_quarter_end(current_time_date)













@user_account_namespace.route('/signup')
class SignUp(Resource):


	@user_account_namespace.expect(signup_model)
	@user_account_namespace.marshal_with(signup_model)
	def post(self):
		"""
			SIGN UP a New User
		"""

		data = user_account_namespace.payload

		try:
			new_user = User(
				email=data.get('email'),
				company_name=data.get('company_name'),
				contact_name=data.get('contact_name'),
				phone=data.get('phone'),
				ein_no=data.get('ein_no'),
				address=data.get('address'),
				city=data.get('city'),
				zipcode=data.get('zipcode'),
				fax=data.get('fax'),
				paid_until = datetime.today() + relativedelta(days = 7),
				password_hash=generate_password_hash(data.get("password"))
			)
			
			new_user.save()



			return "Success", HTTPStatus.CREATED
			
		except:
			return "Error", HTTPStatus.BAD_REQUEST






@user_account_namespace.route('/driver-signup')
class DriverRegister(Resource):


	@jwt_required(refresh=False)
	@user_account_namespace.expect(sign_up_driver_model)
	@user_account_namespace.marshal_with(sign_up_driver_model)
	def post(self):
		"""
			Register a New Driver
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		data = user_account_namespace.payload

		try:
			new_driver = Driver(
				email=data.get('email'),
				first_name=data.get('first_name'),
				last_name=data.get('last_name'),
				cdl_no=data.get('cdl_no'),
				password_hash=generate_password_hash('default123!'),
				user = user.id
			)
			
			new_driver.save()



			return "Success", HTTPStatus.CREATED
			
		except:
			return "Error", HTTPStatus.BAD_REQUEST












@user_account_namespace.route('/login')
class LogIn(Resource):

	
	@user_account_namespace.expect(login_model)
	def post(self):
		"""
			LOGIN And Generate JWT
		"""
		data = request.get_json()

		email = data.get('email')
		password = data.get('password')

		user = User.query.filter_by(email=email).first()
		if user is not None and check_password_hash(user.password_hash, password):
			
			access_token = create_access_token(identity=user.email)
			refresh_token = create_refresh_token(identity=user.email)

			response = {
				'access_token': access_token,
				'refresh_token': refresh_token
			}

			return response, HTTPStatus.OK

		return "Error", HTTPStatus.BAD_REQUEST








@user_account_namespace.route('/driver-login')
class LogIn(Resource):

	
	@user_account_namespace.expect(login_model)
	def post(self):
		"""
			LOGIN Driver And Generate JWT
		"""
		data = request.get_json()

		email = data.get('email')
		password = data.get('password')

		driver = Driver.query.filter_by(email=email).first()

		user = User.query.filter_by(id=driver.user).first()

		if user.paid_until < datetime.today():
			return "Error", HTTPStatus.BAD_REQUEST

		if driver is not None and check_password_hash(driver.password_hash, password):
			
			access_token = create_access_token(identity=driver.email)
			refresh_token = create_refresh_token(identity=driver.email)

			response = {
				'access_token': access_token,
				'refresh_token': refresh_token
			}

			return response, HTTPStatus.OK








@user_account_namespace.route('/refresh-token')
class RefreshToken(Resource):

	
	@jwt_required(refresh=True)
	def post(self):
		"""
			Refresh JWT Token
		"""

		email = get_jwt_identity()

		access_token = create_access_token(identity=email)

		return {"access_token": access_token}, HTTPStatus.OK







@user_account_namespace.route('/check-auth')
class CheckAuth(Resource):

	
	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(user_info_model)
	def get(self):
		"""
			Check if Driver is Logged in and send data of User
		"""

		try:
			email = get_jwt_identity()
			user = User.query.filter_by(email=email).first()


			return user, HTTPStatus.OK

		except:
			return "Error", HTTPStatus.BAD_REQUEST





@user_account_namespace.route('/driver-check-auth')
class CheckAuthDriver(Resource):

	
	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(driver_info_model)
	def get(self):
		"""
			Check if Driver is Logged in and send data of User
		"""

		try:
			email = get_jwt_identity()
			driver = Driver.query.filter_by(email=email).first()

			user = User.query.filter_by(id=driver.user).first()

			if user.paid_until < datetime.today():
				return "Error", HTTPStatus.BAD_REQUEST

			return driver, HTTPStatus.OK

		except:
			return "Error", HTTPStatus.BAD_REQUEST




@user_account_namespace.route('/edit-info')
class EditInfo(Resource):

	
	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(user_info_model)
	def post(self):
		"""
			Edit info in User Account
		"""

		try:
			email = get_jwt_identity()
			user = User.query.filter_by(email=email).first()


			data = request.get_json()
			print(data.get("usa_state"))
			user.contact_name = data.get("contact_name")
			user.company_name = data.get("company_name")
			user.phone = data.get("phone")
			user.ein_no=data.get('ein_no')
			user.address=data.get('address')
			user.city=data.get('city')
			user.zipcode=data.get('zipcode')
			user.fax=data.get('fax')
			user.usa_state = data.get("usa_state")
			user.update()

			return user, HTTPStatus.OK

		except:
			return "Error", HTTPStatus.BAD_REQUEST







@user_account_namespace.route('/reset-password')
class ResetPassword(Resource):

	
	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(user_info_model)
	def post(self):
		"""
			Reset password in User Account
		"""

		try:
			email = get_jwt_identity()
			user = User.query.filter_by(email=email).first()

			data = request.get_json()
			password = data.get('password')
			re_password = data.get("re_password")

			if password != re_password:
				return "Error", HTTPStatus.BAD_REQUEST

			user.password_hash = generate_password_hash(password)

			user.update()

			return user, HTTPStatus.OK

		except:
			return "Error", HTTPStatus.BAD_REQUEST









@user_account_namespace.route('/list-drivers')
class ListDrivers(Resource):

	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(driver_info_model, as_list=True)
	def get(self):
		"""
			List Trucks
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		drivers = Driver.query.filter_by(user=user.id)


		if not drivers.all():
			return None, HTTPStatus.BAD_REQUEST

		return drivers.all(), HTTPStatus.OK





@user_account_namespace.route('/edit-driver/<id>')
class RetrieveEditDeleteDriver(Resource):

	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(driver_info_model)
	def get(self, id):
		"""
			Retrieve Driver Info
		"""

		email = get_jwt_identity()

		user = User.query.filter_by(email=email).first()

		data = request.get_json()

		driver = Driver.query.filter_by(id=id, user=user.id).first()

		return driver, HTTPStatus.OK


	@jwt_required(refresh=False)
	def post(self, id):
		"""
			Edit Driver Info
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		data = request.get_json()

		driver = Driver.query.filter_by(id=id, user=user.id).first()


		driver.first_name = data.get('first_name')
		driver.last_name = data.get('last_name')
		driver.cdl_no = data.get('cdl_no')
		driver.email = data.get('email')
		

		driver.update()

		return "Success", HTTPStatus.OK


	@jwt_required(refresh=False)
	def delete(self, id):
		"""
			Delete Driver Info
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		data = request.get_json()

		driver = Driver.query.filter_by(id=id, user=user.id).first()

		driver.delete()

		return "Success", HTTPStatus.OK












@user_account_namespace.route('/list-trucks')
class ListTrucks(Resource):

	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(truck_info_model, as_list=True)
	def get(self):
		"""
			List Trucks
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		trucks = Truck.query.filter_by(user=user.id)


		if not trucks.all():
			return None, HTTPStatus.BAD_REQUEST

		return trucks.all(), HTTPStatus.OK








@user_account_namespace.route('/create-truck')
class CreateTruck(Resource):

	@jwt_required(refresh=False)
	def post(self):
		"""
			Create New Truck
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		data = request.get_json()

		new_truck = Truck(
			truck_unit = data.get('truck_unit'),
			gross_vehicle_weight = data.get('gross_vehicle_weight'),
			fuel_type = data.get('fuel_type'),
			vim_no = data.get('vim_no'),
			fleet_name = data.get('fleet_name'),
			vehicle_fleet_no = data.get('vehicle_fleet_no'),
			truck_make = data.get('truck_make'),
			truck_model = data.get('truck_model'),
			license_plate_no = data.get('license_plate_no'),
			year = data.get('year'),
			unloaded_vehicle_weight = data.get('unloaded_vehicle_weight'),
			axle = data.get('axle'),
			ny_hut = data.get('ny_hut'),
			or_plate_pass = data.get('or_plate_pass'),
			user = user.id
		)

		new_truck.save()

		return "Success", HTTPStatus.OK


@user_account_namespace.route('/edit-truck/<id>')
class RetrieveEditDeleteTruck(Resource):

	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(truck_info_model)
	def get(self, id):
		"""
			Retrieve Truck Info
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		data = request.get_json()

		truck = Truck.query.filter_by(id=id, user=user.id).first()

		return truck, HTTPStatus.OK


	@jwt_required(refresh=False)
	def post(self, id):
		"""
			Edit Truck Info
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		data = request.get_json()

		truck = Truck.query.filter_by(id=id, user=user.id).first()

		truck.truck_unit = data.get('truck_unit')
		truck.gross_vehicle_weight = data.get('gross_vehicle_weight')
		truck.fuel_type = data.get('fuel_type')
		truck.vim_no = data.get('vim_no')
		truck.fleet_name = data.get('fleet_name')
		truck.vehicle_fleet_no = data.get('vehicle_fleet_no')
		truck.truck_make = data.get('truck_make')
		truck.truck_model = data.get('truck_model')
		truck.license_plate_no = data.get('license_plate_no')
		truck.year = data.get('year')
		truck.unloaded_vehicle_weight = data.get('unloaded_vehicle_weight')
		truck.axle = data.get('axle')
		truck.ny_hut = data.get('ny_hut')
		truck.or_plate_pass = data.get('or_plate_pass')

		if data.get('current_driver'):
			driver = Driver.query.filter_by(email=data.get('current_driver'), user=user.id).first()
			truck.current_driver = driver.id
		

		truck.update()

		return "Success", HTTPStatus.OK


	@jwt_required(refresh=False)
	def delete(self, id):
		"""
			Delete Truck Info
		"""

		email = get_jwt_identity()
		user = User.query.filter_by(email=email).first()

		data = request.get_json()

		truck = Truck.query.filter_by(id=id, user=user.id).first()

		truck.delete()

		return "Success", HTTPStatus.OK



@user_account_namespace.route('/extend-service')
class ExtendService(Resource):

	@jwt_required(refresh=False)
	def post(self):

		try:

			stripe.api_key = current_app.config["STRIPE_TEST_SECRET_KEY"]

			email = get_jwt_identity()
			user = User.query.filter_by(email=email).first()
			
			data = request.get_json()

			card_num = data.get("card_num")
			exp_month = data.get("exp_month")
			exp_year = data.get("exp_year")
			cvc = data.get("cvc")

			token = stripe.Token.create(
				card = {
					"number": card_num,
					"exp_month": exp_month,
					"exp_year": exp_year,
					"cvc": cvc
				}
			)

			amount = 2500

			charge = stripe.Charge.create(
				amount=amount,
				currency="usd",
				source=token
			)

			stripe_charge_id = charge['id']

			new_payment = Payment(
				amount = amount,
				charge_id = stripe_charge_id,
				user = user.id
			)

			new_payment.save()

			
			user.paid_until = add_paid_quarters(1, datetime.today())

			user.update()

			return "Success", HTTPStatus.OK



		except:
			return "Error during payment", HTTPStatus.BAD_REQUEST


















@user_account_namespace.route('/driver')
class RetrieveDriverInfo(Resource):

	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(driver_info_model)
	def get(self):
		"""
			Retrieve Driver Info
		"""

		email = get_jwt_identity()
		
		driver = Driver.query.filter_by(email=email).first()

		return driver, HTTPStatus.OK		


	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(driver_info_model)
	def post(self):
		"""
			Edit Driver Info
		"""	

		email = get_jwt_identity()

		driver = Driver.query.filter_by(email=email).first()

		data = request.get_json()


		driver.first_name = data.get('first_name')
		driver.last_name = data.get('last_name')
		driver.cdl_no = data.get('cdl_no')
		

		driver.update()

		return driver, HTTPStatus.OK





@user_account_namespace.route('/current-truck')
class RetrieveCurrentTruck(Resource):

	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(truck_info_model)
	def get(self):
		"""
			Retrieve Current Truck
		"""

		email = get_jwt_identity()
		
		driver = Driver.query.filter_by(email=email).first()
		truck = Truck.query.filter_by(current_driver = driver.id).first()

		return truck, HTTPStatus.OK		


	@jwt_required(refresh=False)
	@user_account_namespace.marshal_with(truck_info_model)
	def post(self):
		"""
			Change Current Truck
		"""	

		email = get_jwt_identity()

		driver = Driver.query.filter_by(email=email).first()

		data = request.get_json()

		new_truck_plate = data.get('license_plate_no')
		truck = Truck.query.filter_by(license_plate_no=new_truck_plate, user = driver.user).first()

		if truck:
			try:
				old_truck = Truck.query.filter_by(current_driver = driver.id).first()
				old_truck.current_driver = None
				old_truck.update()
				truck.current_driver = driver.id
			except:
				truck.current_driver = driver.id
		
			truck.update()

		else:
			return "Error", HTTPStatus.BAD_REQUEST


		return truck, HTTPStatus.OK





def send_async_email(app, msg):
    from api import mail
    with app.app_context():
        for i in range(5, -1, -1):
            sleep(2)
            print('time:', i)
        from api import mail
        mail.send(msg)




@user_account_namespace.route('/send-request-reset-password')
class SendRequestResetPassword(Resource):

	def post(self):
		
		app = current_app._get_current_object()

		data = request.get_json()

		try:
			user = User.query.filter_by(email=data.get('email')).first()
			email_in_bytes = bytes(user.email, 'utf-8')
			last_uid_password = base64.urlsafe_b64encode(email_in_bytes)
			last_uid_password = last_uid_password.decode('UTF-8')
			user.last_token_password = secrets.token_hex(16)
			user.update()

			msg = flask_mail.Message('Reset Password Requested', sender=current_app.config['MAIL_USERNAME'], recipients=[
                             user.email])

			msg.msId = msg.msgId.split('@')[0] + '@' + current_app.config["MAIL_STRING_ID"]

			msg.html = render_template("user-account/send-request-reset-password.html",uid=last_uid_password, token=user.last_token_password)

			thr = Thread(target=send_async_email, args=[app, msg])
			thr.start()
			return "Success", HTTPStatus.OK
		except:
			return "Error", HTTPStatus.BAD_REQUEST



@user_account_namespace.route('/reset-password/<uid>/<token>')
class ResetPassword(Resource):

	def post(self, uid, token):
		
		app = current_app._get_current_object()

		data = request.get_json()

		password = data.get('password')
		re_password = data.get('re_password')

		if(password != re_password):
			return "Error", HTTPStatus.BAD_REQUEST

		# try:
		if True:
			email_in_bytes = bytes(uid, 'utf-8')
			last_uid_password = base64.urlsafe_b64decode(email_in_bytes)
			email = last_uid_password.decode('UTF-8')

			print(email)

			user = User.query.filter_by(email=email, last_token_password=token).first()

			user.last_token_password = "-1"
			user.password_hash = generate_password_hash(password)
			user.update()

			return "Success", HTTPStatus.OK
		# except:
		else:
			return "Error", HTTPStatus.BAD_REQUEST



@user_account_namespace.route('/driver/send-request-reset-password')
class DriverSendRequestResetPassword(Resource):

	def post(self):
		
		app = current_app._get_current_object()

		data = request.get_json()

		try:
			driver = Driver.query.filter_by(email=data.get('email')).first()
			email_in_bytes = bytes(driver.email, 'utf-8')
			last_uid_password = base64.urlsafe_b64encode(email_in_bytes)
			last_uid_password = last_uid_password.decode('UTF-8')
			driver.last_token_password = secrets.token_hex(16)
			driver.update()

			msg = flask_mail.Message('Reset Password Requested', sender=current_app.config['MAIL_USERNAME'], recipients=[
                             driver.email])

			msg.msId = msg.msgId.split('@')[0] + '@' + current_app.config["MAIL_STRING_ID"]

			msg.html = render_template("user-account/driver-send-request-reset-password.html",uid=last_uid_password, token=driver.last_token_password)

			thr = Thread(target=send_async_email, args=[app, msg])
			thr.start()
			return "Success", HTTPStatus.OK
		except:
			return "Error", HTTPStatus.BAD_REQUEST


@user_account_namespace.route('/driver/reset-password/<uid>/<token>')
class DriverResetPassword(Resource):

	def post(self, uid, token):
		
		app = current_app._get_current_object()

		data = request.get_json()

		password = data.get('password')
		re_password = data.get('re_password')

		if(password != re_password):
			return "Error", HTTPStatus.BAD_REQUEST

		# try:
		if True:
			email_in_bytes = bytes(uid, 'utf-8')
			last_uid_password = base64.urlsafe_b64decode(email_in_bytes)
			email = last_uid_password.decode('UTF-8')

			print(email)

			driver = Driver.query.filter_by(email=email, last_token_password=token).first()

			driver.last_token_password = "-1"
			driver.password_hash = generate_password_hash(password)
			driver.update()

			return "Success", HTTPStatus.OK
		# except:
		else:
			return "Error", HTTPStatus.BAD_REQUEST		

