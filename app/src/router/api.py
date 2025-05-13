from fastapi import APIRouter
# from app.src.router.root import api as root
from app.src.router.user import api as user
from app.src.router.download import api as download
from app.src.router.customer import api as customer
from app.src.router.receipt import api as receipt
from app.src.router.ai import api as ai
from app.src.router.transaction import api as transaction
from app.src.router.category import api as category
from app.src.router.report import api as report

router = APIRouter()

# router.include_router(root.router, tags=["Root"], prefix="/root")
router.include_router(user.router, tags=["User"], prefix="/user")
router.include_router(download.router, tags=["Download"], prefix="/download")
router.include_router(customer.router, tags=["Customer"], prefix="/customer")
router.include_router(receipt.router, tags=["Receipt"], prefix="/receipt")
router.include_router(ai.router, tags=["AI"], prefix="/ai")
router.include_router(transaction.router, tags=[
                      "Transaction"], prefix="/transaction")
router.include_router(category.router, tags=["Category"], prefix="/category")
router.include_router(report.router, tags=["Report"], prefix="/report")
