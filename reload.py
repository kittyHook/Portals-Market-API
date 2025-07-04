# main.py
from fastapi import FastAPI, APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import httpx

API_BASE = "https://portals-market.com/api"


app = FastAPI(title="Portals Market Proxy API")
router = APIRouter(prefix="/market", tags=["market"])


client: Optional[httpx.AsyncClient] = None

@app.on_event("startup")
async def startup_event():
    global client
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "Authorization": (
            ""
        ),
        "Referer": "https://portals-market.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }
    client = httpx.AsyncClient(
        base_url=API_BASE,
        headers=headers,
        timeout=10.0
    )

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

# 1. /market/config
class ConfigResponse(BaseModel):
    commission: str
    user_cashback: str
    deposit_wallet: str
    usdt_course: str

@router.get("/config", response_model=ConfigResponse)
async def get_config():
    resp = await client.get("/market/config")
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch config")
    return resp.json()


# 2. /market/wallets/limits
class WalletLimits(BaseModel):
    max_per_transaction: str
    max_daily: str
    daily_used: str
    daily_remaining: str

@router.get("/wallets/limits", response_model=WalletLimits)
async def get_wallet_limits():
    resp = await client.get("/users/wallets/limits")
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch wallet limits")
    return resp.json()


# 3. /market/wallets/history
class NFTAttribute(BaseModel):
    type: str
    value: Any
    rarity_per_mille: float

class NFTInfo(BaseModel):
    id: str
    name: str
    photo_url: Optional[str]
    collection_id: str
    external_collection_number: int
    status: str
    animation_url: Optional[str]
    has_animation: bool
    attributes: List[NFTAttribute]
    emoji_id: Optional[str]
    is_owned: Optional[bool]
    floor_price: Optional[str]

class WalletAction(BaseModel):
    type: str
    from_wallet: str
    added_at: str
    amount: str
    tx_hash: Optional[str]
    tx_lt: Optional[str]
    balance_before: str
    balance_after: str
    related_entity_id: Optional[str]
    related_entity_type: Optional[str]
    description: str
    nft: Optional[NFTInfo]

class WalletHistoryResponse(BaseModel):
    actions: List[WalletAction]

@router.get("/wallets/history", response_model=WalletHistoryResponse)
async def get_wallet_history(
    offset: int = Query(0, ge=0),
    limit: int = Query(30, ge=1),
    types: Optional[str] = Query(None, description="Comma-separated types")
):
    params = {"offset": offset, "limit": limit}
    if types:
        params["types"] = types
    resp = await client.get("/users/wallets/history", params=params)
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch wallet history")
    return resp.json()


# 4. /market/wallets/balance
class WalletBalance(BaseModel):
    balance: str
    frozen_funds: str

@router.get("/wallets/balance", response_model=WalletBalance)
async def get_wallet_balance():
    resp = await client.get("/users/wallets/")
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch wallet balance")
    return resp.json()


# 5. /market/nfts
class NFTItem(BaseModel):
    id: str
    tg_id: str
    collection_id: str
    external_collection_number: int
    name: str
    photo_url: Optional[str]
    price: Optional[str]
    attributes: List[NFTAttribute]
    listed_at: str
    status: str
    animation_url: Optional[str]
    emoji_id: Optional[str]
    has_animation: bool
    unlocks_at: str

class NFTListResponse(BaseModel):
    nfts: List[NFTItem]

@router.get("/nfts", response_model=NFTListResponse)
async def list_nfts():
    resp = await client.get("/nfts")
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to list NFTs")
    return resp.json()


# 6. /market/nfts/search
@router.get("/nfts/search", response_model=Any)
@router.get("/nfts/search", response_model=Any)
async def search_nfts(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    filter_by_collections: Optional[str] = None,
    filter_by_backdrops: Optional[str] = None,
    filter_by_symbols: Optional[str] = None,
    filter_by_models: Optional[str] = None,  
    sort_by: str = Query("price asc"),
    status: str = Query("listed")
):
    params = {
        "offset": offset,
        "limit": limit,
        "sort_by": sort_by,
        "status": status,
    }
    if filter_by_collections:
        params["filter_by_collections"] = filter_by_collections
    if filter_by_backdrops:
        params["filter_by_backdrops"] = filter_by_backdrops
    if filter_by_symbols:
        params["filter_by_symbols"] = filter_by_symbols
    if filter_by_models:
        params["filter_by_models"] = filter_by_models  

    resp = await client.get("/nfts/search", params=params)
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to search NFTs")
    return resp.json()

# 7. /market/collections/backdrops
class Backdrop(BaseModel):
    name: str
    url: str
    centerColor: int
    edgeColor: int
    patternColor: int
    textColor: int
    rarityPermille: float
    hex: dict

@router.get("/collections/backdrops", response_model=List[Backdrop])
async def get_backdrops():
    resp = await client.get("/collections/filters/backdrops")
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch backdrops")
    return resp.json()


# 8. /market/collections/backdrops/floor
class FloorPricesResponse(BaseModel):
    floorPrices: dict

@router.get("/collections/backdrops/floor", response_model=FloorPricesResponse)
async def get_backdrops_floor():
    resp = await client.get("/collections/filters/backdrops/floor")  # если такой эндпоинт есть
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch floor prices")
    return resp.json()


# 9. /market/nfts/buy и /market/nfts/withdraw
class BuyPayload(BaseModel):
    nft_details: List[dict] = Field(..., example=[{"id": "uuid", "price": "1.23"}])

@router.post("/nfts/buy", response_model=Any)
async def buy_nfts(payload: BuyPayload):
    resp = await client.post("/nfts", json=payload.dict())
    if resp.status_code not in (200, 201):
        raise HTTPException(resp.status_code, "Failed to buy NFT(s)")
    return resp.json()

class WithdrawPayload(BaseModel):
    gift_ids: List[str]

@router.post("/nfts/withdraw", response_model=Any)
async def withdraw_nfts(payload: WithdrawPayload):
    resp = await client.post("/nfts/withdraw", json=payload.dict())
    if resp.status_code not in (200, 201):
        raise HTTPException(resp.status_code, "Failed to withdraw NFT(s)")
    return resp.json()


# 10. /market/users/actions
class UserActionMetadata(BaseModel):
    seller_revenue: Optional[str]
    cashback_amount: Optional[str]

class UserAction(BaseModel):
    initiator_user_id: int
    nft_id: str
    offer_id: Optional[str]
    type: str
    amount: str
    created_at: str
    referrer_revenue: Optional[str]
    collection_id: str
    metadata: UserActionMetadata
    nft: Optional[NFTInfo]

class UserActionsResponse(BaseModel):
    actions: List[UserAction]

@router.get("/users/actions", response_model=UserActionsResponse)
async def get_user_actions(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1)
):
    resp = await client.get("/users/actions/", params={"offset": offset, "limit": limit})
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch user actions")
    return resp.json()


app.include_router(router)