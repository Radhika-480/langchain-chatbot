# tools.py

from langchain.tools import tool
from datetime import datetime
from db import db # Mongo collection

from langchain.tools import tool
from typing import List, Annotated

@tool
def add_contract_tool(
    vendor_name: str,
    vendor_email: str,
    phone: str,
    address: str,
    pincode: str,
    business_type: str,
    gst_number: str,
    tax: float,
    product_name: str,
    quantity: int,
    unit: str,
    category: str,
    sub_category: str,
    tags: Annotated[List[str], "List of tags related to the product"],  # ✅ Gemini needs this!
    warranty_tenure: int,
    warranty_unit: str,
    date_of_delivery: str,
    returnable: bool,
    return_conditions: Annotated[List[str], "List of return conditions like accepted, unused"],  # ✅ Required!
    status: str,
    store_id: str = "ST001",
    org_id: str = "ORG001"
) -> str:
   
# @tool
# def add_contract_tool(
#     vendor_name: str,
#     vendor_email: str,
#     phone: str,
#     address: str,
#     pincode: str,
#     business_type: str,
#     gst_number: str,
#     tax: float,
#     product_name: str,
#     quantity: int,
#     unit: str,
#     category: str,
#     sub_category: str,
#     tags: list,
#     warranty_tenure: int,
#     warranty_unit: str,
#     date_of_delivery: str,
#     returnable: bool,
#     return_conditions: list,
#     status: str,
#     store_id: str = "ST001",  # temp static (in real: pass from token/session)
#     org_id: str = "ORG001"
# ) -> str:
    """
    Adds a vendor contract to MongoDB directly (no internal API call).
    """
    try:
        total_contracts = db.Contracts.count_documents({})
        contract_id = f"C{total_contracts + 1:03}"

        payload = {
            "contract_id": contract_id,
            "store_id": store_id,
            "org_id": org_id,
            "vendor_name": vendor_name,
            "vendor_email": vendor_email,
            "phone": phone,
            "address": address,
            "pincode": pincode,
            "business_type": business_type,
            "gst_number": gst_number,
            "tax": tax,
            "product_name": product_name,
            "quantity": quantity,
            "unit": unit,
            "category": category,
            "sub_category": sub_category,
            "tags": tags,
            "warranty_tenure": warranty_tenure,
            "warranty_unit": warranty_unit,
            "date_of_delivery": date_of_delivery,
            "returnable": returnable,
            "return_conditions": return_conditions,
            "status": status,
            "created_at": datetime.now()
        }

        db.insert_one(payload)

        return f"Contract {contract_id} created successfully."
    except Exception as e:
        return f"Error saving contract: {str(e)}"
