from model.asset_data import AssetData


def test_asset_creation_noargs():
    asset = AssetData()
    assert asset.qty == 0.0
    assert asset.price == 0.0
    assert asset.total == 0.0


def test_asset_creation_allargs():
    asset = AssetData(2, 3, 6)
    assert asset.qty == 2.0
    assert asset.price == 3.0
    assert asset.total == 6.0


def test_asset_creation_no_total():
    asset = AssetData(2, 3)
    assert asset.qty == 2.0
    assert asset.price == 3.0
    assert asset.total == 6.0


def test_set_total_on_qty():
    asset = AssetData(20, 3)
    asset.qty = 20
    assert asset.total == 60


def test_set_total_on_price():
    asset = AssetData(5)
    asset.price = 10
    assert asset.total == 50
