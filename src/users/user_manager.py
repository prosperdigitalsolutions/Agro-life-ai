"""
AGRO LIFE-AI
User Management Module

Research Prototype

Supports:
- Farmer users
- Customer users
- User registration
- User lookup
- User validation
"""


from typing import Optional

from src.database.database_manager import (
    add_user,
    get_user,
)


SUPPORTED_USER_TYPES = {
    "farmer",
    "customer",
}


def validate_user_type(user_type: str) -> str:
    """
    Validate and standardize the user type.
    """

    if not isinstance(user_type, str):
        raise ValueError("User type must be a text value.")

    normalized_type = user_type.strip().lower()

    if normalized_type not in SUPPORTED_USER_TYPES:
        raise ValueError(
            "Unsupported user type. "
            "Use 'farmer' or 'customer'."
        )

    return normalized_type


def register_user(
    full_name: str,
    user_type: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
):
    """
    Register a farmer or customer in AGRO LIFE-AI.

    Returns
    -------
    int
        Newly created user ID.
    """

    if not isinstance(full_name, str) or not full_name.strip():
        raise ValueError("Full name cannot be empty.")

    normalized_name = full_name.strip()
    normalized_type = validate_user_type(user_type)

    user_id = add_user(
        full_name=normalized_name,
        user_type=normalized_type,
        phone=phone,
        email=email,
    )

    return user_id


def get_user_profile(user_id: int):
    """
    Retrieve a user profile using the database user ID.
    """

    if not isinstance(user_id, int):
        raise ValueError("User ID must be an integer.")

    if user_id <= 0:
        raise ValueError("User ID must be greater than zero.")

    user = get_user(user_id)

    if user is None:
        raise ValueError(
            f"No user was found with User ID {user_id}."
        )

    return user


def display_user_profile(user):
    """
    Display a user profile in a readable format.
    """

    print()
    print("=" * 70)
    print("AGRO LIFE-AI USER PROFILE")
    print("=" * 70)

    print(f"User ID: {user[0]}")
    print(f"Full Name: {user[1]}")
    print(f"User Type: {user[2]}")
    print(f"Phone: {user[3]}")
    print(f"Email: {user[4]}")
    print(f"Created At: {user[5]}")

    print("=" * 70)


def display_registration_result(
    user_id: int,
    full_name: str,
    user_type: str,
):
    """
    Display registration confirmation.
    """

    print()
    print("=" * 70)
    print("AGRO LIFE-AI USER REGISTRATION")
    print("=" * 70)

    print(f"Registration Successful")
    print(f"User ID: {user_id}")
    print(f"Full Name: {full_name}")
    print(f"User Type: {user_type}")

    print("=" * 70)


if __name__ == "__main__":

    print("=" * 70)
    print("AGRO LIFE-AI USER MANAGEMENT TEST")
    print("=" * 70)

    # ----------------------------------------------------------
    # TEST 1: REGISTER FARMER
    # ----------------------------------------------------------

    print()
    print("TEST 1: FARMER REGISTRATION")
    print("-" * 70)

    farmer_id = register_user(
        full_name="Test Farmer",
        user_type="farmer",
        phone="0970000001",
        email="farmer@test.agrolife.ai",
    )

    display_registration_result(
        user_id=farmer_id,
        full_name="Test Farmer",
        user_type="farmer",
    )

    # ----------------------------------------------------------
    # TEST 2: RETRIEVE FARMER
    # ----------------------------------------------------------

    print()
    print("TEST 2: FARMER PROFILE RETRIEVAL")
    print("-" * 70)

    farmer = get_user_profile(farmer_id)

    display_user_profile(farmer)

    # ----------------------------------------------------------
    # TEST 3: REGISTER CUSTOMER
    # ----------------------------------------------------------

    print()
    print("TEST 3: CUSTOMER REGISTRATION")
    print("-" * 70)

    customer_id = register_user(
        full_name="Test Customer",
        user_type="customer",
        phone="0970000002",
        email="customer@test.agrolife.ai",
    )

    display_registration_result(
        user_id=customer_id,
        full_name="Test Customer",
        user_type="customer",
    )

    # ----------------------------------------------------------
    # TEST 4: RETRIEVE CUSTOMER
    # ----------------------------------------------------------

    print()
    print("TEST 4: CUSTOMER PROFILE RETRIEVAL")
    print("-" * 70)

    customer = get_user_profile(customer_id)

    display_user_profile(customer)

    # ----------------------------------------------------------
    # TEST 5: INVALID USER TYPE
    # ----------------------------------------------------------

    print()
    print("TEST 5: INVALID USER TYPE")
    print("-" * 70)

    try:
        register_user(
            full_name="Invalid Test User",
            user_type="admin",
        )

        print("ERROR: Invalid user type was accepted.")

    except ValueError as error:
        print("Invalid user type rejected correctly.")
        print(f"Message: {error}")

    # ----------------------------------------------------------
    # FINAL RESULT
    # ----------------------------------------------------------

    print()
    print("=" * 70)
    print("USER MANAGEMENT TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)