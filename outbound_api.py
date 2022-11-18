from typing import List
from datetime import date
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import requests
import json


class Contact(BaseModel):
    contactTypeCode: str
    departmentName: str


class Buyer(BaseModel):
    primaryId: str
    contact: List[Contact]


class AddressSupp(BaseModel):
    name: str
    city: str
    countryCode: str
    postalCode: str
    streetAddressOne: str
    languageOfThePartyCode: str


class Supplier(BaseModel):
    primaryId: str
    address: AddressSupp


class AddressBill(BaseModel):
    name: str
    city: str
    countryCode: str
    postalCode: str
    streetAddressOne: str
    languageOfThePartyCode: str


class BillTo(BaseModel):
    primaryId: str
    address: AddressBill


class AddressShip(BaseModel):
    name: str
    city: str
    countryCode: str
    postalCode: str
    streetAddressOne: str
    languageOfThePartyCode: str


class ShipTo(BaseModel):
    primaryId: str
    address: AddressShip


class ShipFrom(BaseModel):
    primaryId: str


class OrderLogisticalInformation(BaseModel):
    shipTo: ShipTo
    shipFrom: ShipFrom


class MonetaryAmount(BaseModel):
    value: int
    currencyCode: str


class NetPrice(BaseModel):
    value: int


class RequestedQuantity(BaseModel):
    value: int
    measurementUnitCode: str


class TransactionalTradeItem(BaseModel):
    primaryId: str


class RequestedShipDateTime(BaseModel):
    date: date


class RequestedDeliveryDateTime(BaseModel):
    date: date


class OrderLogisticalDate(BaseModel):
    requestedShipDateTime: RequestedShipDateTime
    requestedDeliveryDateTime: RequestedDeliveryDateTime


class ShipToLineLevel(BaseModel):
    primaryId: str


class ShipFromLineLevel(BaseModel):
    primaryId: str


class OrderLogisticalLineItem(BaseModel):
    shipTo: ShipToLineLevel
    shipFrom: ShipFromLineLevel
    orderLogisticalDateInformation: OrderLogisticalDate


class RequestedQuantityDetail(BaseModel):
    value: float
    measurementUnitCode: str


class RequestedDeliveryDateTimeDetail(BaseModel):
    date: date


class OrderLogisticalDateDetail(BaseModel):
    requestedDeliveryDateTime: RequestedDeliveryDateTimeDetail = None


class OrderLogisticalInformationDetail(BaseModel):
    orderLogisticalDateInformation: OrderLogisticalDateDetail = None


class LineItemDetail(BaseModel):
    scheduleNumber: str
    requestedQuantity: RequestedQuantityDetail
    orderLogisticalInformation: OrderLogisticalInformationDetail


class TotalReceivedQuantity(BaseModel):
    value: float
    measurementUnitCode: str


class LineItem(BaseModel):
    lineItemNumber: int
    itemFamily: str
    lineStatus: str
    lineItemDetail: List[LineItemDetail] = None
    netPrice: NetPrice
    requestedQuantity: RequestedQuantity
    transactionalTradeItem: TransactionalTradeItem
    orderLogisticalInformation: OrderLogisticalLineItem
    totalReceivedQuantity: TotalReceivedQuantity = None


class AVPList(BaseModel):
    name: str
    value: str


class LoadPO(BaseModel):
    orderId: str
    buyer: Buyer
    supplier: Supplier
    billTo: BillTo
    orderLogisticalInformation: OrderLogisticalInformation
    orderTypeCode: str
    totalMonetaryAmountIncludingTaxes: MonetaryAmount
    orderSubType: str
    lineItem: List[LineItem]
    avpList: List[AVPList]


app = FastAPI()


@app.post("/frv_load_po", status_code=status.HTTP_202_ACCEPTED)
def create_upload_file(load_po: LoadPO):
    try:
        response = requests.post(
            os.getenv("FRV_API_KEY"),
            json=json.loads(load_po.json()),
            auth=(os.getenv("FRV_USER_NAME"), os.getenv("FRV_PASSWORD"))
        )

    except requests.exceptions.SSLError:
        return "couldn't connect with Fareva server"

    if response.status_code == 202:
        return "Succesfully processed."
    else:
        error_detail = HTTPException(
            status_code=502,
            detail=f"Error {response.status_code} on Fareva API: {response.text}"
        )
        return error_detail


@app.post("/lct_loadplan", status_code=status.HTTP_202_ACCEPTED)
def upload_load_plan_to_lct(loadplan: dict):
    response = requests.post(
        os.getenv("LCT_API_KEY"),
        json=json.loads(loadplan.json()),
        auth=(os.getenv("LCT_USER_NAME"), os.getenv("LCT_PASSWORD"))
    )
    if response.status_code == 202:
        return "Succesfully processed."
    else:
        return HTTPException(
            status_code=502,
            detail=f"Error {response.status_code} on LCT API: {response.text}")
