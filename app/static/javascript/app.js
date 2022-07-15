const addItemBtn = document.querySelector('#add-btn');
const newItemModal = document.querySelector('#new-item-modal');
const claimItemBtns = document.getElementsByClassName("claim-btn");
const claimItemModal = document.querySelector('#claim-item-modal');
const returnItemBtns = document.getElementsByClassName("return-btn");
const returnItemModal = document.querySelector('#return-item-modal');
const newWarehouseBtn = document.querySelector("#new-warehouse-btn");
const newWarehouseModal = document.querySelector('#new-warehouse-modal');
const renameItemBtn = document.querySelector("#rename-item-btn");
const renameItemModal = document.querySelector('#rename-item-modal');
const deleteItemBtn = document.querySelector("#delete-item-btn");
const deleteItemModal = document.querySelector('#delete-item-modal');
const deleteWarehouseBtn = document.querySelector("#delete-warehouse-btn");
const deleteWarehouseModal = document.querySelector('#delete-warehouse-modal');

const searchInput = document.querySelector('#searchbar');
const items = document.getElementsByClassName("item");

let active_modal;

window.onclick = function (event) {
    if (event.target == active_modal) {
        active_modal.classList.remove("bg-active");
    }
}

for (let i = 0; i < returnItemBtns.length; i++) {
    returnItemBtns[i].addEventListener("click", function () {
        let id = this.getAttribute("data-id");
        let itemname = this.getAttribute("data-itemname");
        active_modal = returnItemModal;
        active_modal.classList.add('bg-active');
        document.querySelector('#return-item-itemname').innerHTML = itemname;
        document.querySelector('#return-item-id').setAttribute("value", id);
    });
}


for (let i = 0; i < claimItemBtns.length; i++) {
    claimItemBtns[i].addEventListener("click", function () {
        let id = this.getAttribute("data-id");
        let itemname = this.getAttribute("data-itemname");
        let owner = this.getAttribute("data-owner");
        console.log(owner);
        active_modal = claimItemModal;
        active_modal.classList.add('bg-active');
        document.querySelector('#claim-item-owner').setAttribute("value", owner);
        document.querySelector('#claim-item-itemname').innerHTML = itemname;
        document.querySelector('#claim-item-owner-title').innerHTML = owner;
        document.querySelector('#claim-item-id').setAttribute("value", id);
    });
}


addItemBtn.addEventListener('click', function () {
    active_modal = newItemModal;
    active_modal.classList.add('bg-active');
})

newWarehouseBtn.addEventListener('click', function () {
    active_modal = newWarehouseModal;
    active_modal.classList.add('bg-active');
})


searchInput.addEventListener('input', function (evt) {
    search(this.value);
});

function search(a) {
    for (let i = 0; i < items.length; i++) {
        if (!items[i].querySelector('.item_name').textContent.toLowerCase().includes(a.toLowerCase())) {
            items[i].style.display = "none";
        } else {
            items[i].style.display = null;
        }
    }
}

if (renameItemBtn) {
    renameItemBtn.addEventListener('click', function () {
        active_modal = renameItemModal;
        active_modal.classList.add('bg-active');
        let itemname = document.querySelector('.item_name').textContent;
        document.querySelector('#rename-item-name').textContent = itemname;
        document.querySelector('#old-item-name').setAttribute("value", itemname);
    })
}

if (deleteItemBtn) {
    deleteItemBtn.addEventListener('click', function () {
        active_modal = deleteItemModal;
        active_modal.classList.add('bg-active');
        let itemname = document.querySelector('.item_name').textContent;
        document.querySelector('#delete-item-name-text').textContent = itemname;
        document.querySelector('#delete-item-name-form').setAttribute("value", itemname);
    })
}

if (deleteWarehouseBtn) {
    deleteWarehouseBtn.addEventListener('click', function () {
        active_modal = deleteWarehouseModal;
        active_modal.classList.add('bg-active');
        let warehouse_name = document.querySelector('.item_owner_name').textContent;
        document.querySelector('#delete-warehouse-name-text').textContent = warehouse_name;
        document.querySelector('#delete-warehouse-name-form').setAttribute("value", warehouse_name);
    })
}