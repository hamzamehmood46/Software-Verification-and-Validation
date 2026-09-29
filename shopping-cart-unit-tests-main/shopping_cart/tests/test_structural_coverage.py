from orders import Order, Item, calculate_total
import pytest





def test_struct_multiple_items_loop():
    order = Order()
    order.add_item(Item("A", 1.11, 1))
    order.add_item(Item("B", 2.22, 2))
    assert order.calculate_subtotal() == pytest.approx(5.55, rel=1e-9, abs=1e-9)



def test_struct_amount_clamped_to_zero():
    assert calculate_total(5, 0, 10, 0.5) == 0.00



def test_struct_large_tax_percent():
    assert calculate_total(10, 0, 0, 1.0) == 20.00



def test_struct_reward_points_zero(mocker):
    order = Order()
    mocker.patch.object(order, "calculate_order_total", return_value=0)
    assert order.get_reward_points() == 0