function togglePassword(eye, inputId) {
    const pass = document.getElementById(inputId);
    if (pass.type === "password") {
        pass.type = "text";
        eye.src = "static/images/eye-open.png";
    } else {
        pass.type = "password";
        eye.src = "static/images/eye-close.png";
    }
}

function showSignUp() {
        document.getElementById("container").classList.add("active");
    }

function showSignIn() {
    document.getElementById("container").classList.remove("active");
}

function deleteModal(productId) {
    const modal = document.querySelector(".delete-modal");
    const confirmBtn = document.getElementById("confirmDelete");

    // set dynamic delete URL
    confirmBtn.href = `/delete/${productId}`;

    modal.style.display = "flex";
}

function closeModal() {
    document.querySelector(".delete-modal").style.display = "none";
}

async function editModal(id) {
    const modal = document.querySelector(".update-modal");
    const form = document.getElementById("updateForm");

    try {
        const res = await fetch(`/get_item/${id}`);
        const data = await res.json();

        console.log("Response:", data); 

        if (data.error) {
            alert("Item not found");
            return;
        }

        // Set correct form action
        form.action = `/update/${data.id}`;

        // Fill inputs
        document.getElementById("editName").value = data.name;
        document.getElementById("editBrand").value = data.brand;
        document.getElementById("editCategory").value = data.category;
        document.getElementById("editDescription").value = data.description;

        document.getElementById("editQuantity").value = data.quantity;
        document.getElementById("editUnit").value = data.unit;
        document.getElementById("editReorderLevel").value = data.reorder_level;

        document.getElementById("editWarehouse").value = data.warehouse;
        document.getElementById("editAisle").value = data.aisle;
        document.getElementById("editRack").value = data.rack;
        document.getElementById("editBin").value = data.bin;

        document.getElementById("editCost").value = data.cost;
        document.getElementById("editSellingPrice").value = data.selling_price;
        

        modal.style.display = "block";

    } catch (err) {
        console.error(err);
        alert("Error loading item");
    }
}

function closeEditModal() {
    document.querySelector(".update-modal").style.display = "none";
}

