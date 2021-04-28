from app.models.sqa_models import Symbol
from app.db.tasks import SESSION,ASYNC_SESSION
from sqlalchemy_paginator import Paginator
from app.helpers.database_helper import bulk_insert


class SymbolController(Symbol):


	def __init__(self):


		self.session=ASYNC_SESSION



	def bulk_insert_data(self,data_dict):

		try:

			with self.session() as ses:

			await session.run_sync(bulk_insert,data_dict,Symbol)

			await session.commit()

		except Exception as e:

			print("Error Inserting Data ERROR DETAILS {e}")


		finally:

			session.close()


	def get_symbols():
