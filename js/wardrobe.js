document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('file-preview');
    const uploadButton = document.getElementById('uploadButton');
    const wardrobeGrid = document.getElementById('wardrobeGrid');

    // Wardrobe items storage
    let wardrobeItems = JSON.parse(localStorage.getItem('wardrobeItems')) || [];

    // File Preview and Drag & Drop
    function handleFiles(files) {
        filePreview.innerHTML = ''; // Clear previous previews
        
        Array.from(files).forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const previewImg = document.createElement('img');
                    previewImg.src = e.target.result;
                    filePreview.appendChild(previewImg);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Upload Button Handler
    uploadButton.addEventListener('click', () => {
        const files = fileInput.files;
        const category = document.getElementById('categorySelect').value;
        const itemName = document.getElementById('itemName').value;
        const color = document.getElementById('colorInput').value;

        if (files.length === 0) {
            alert('Please select an image');
            return;
        }

        Array.from(files).forEach(file => {
            const reader = new FileReader();
            reader.onload = function(event) {
                const newItem = {
                    id: Date.now(), // unique identifier
                    imageUrl: event.target.result,
                    category,
                    itemName,
                    color
                };

                // Add to wardrobe items
                wardrobeItems.push(newItem);
                
                console.log('New item added:', newItem); // Log the new item
                localStorage.setItem('wardrobeItems', JSON.stringify(wardrobeItems));

                console.log('Current wardrobe items before rendering:', wardrobeItems); // Log current items before rendering
                renderWardrobeItems();
            };

            reader.readAsDataURL(file);
        });

        // Reset form and previews
        fileInput.value = '';
        filePreview.innerHTML = '';
        document.getElementById('categorySelect').selectedIndex = 0;
        document.getElementById('itemName').value = '';
        document.getElementById('colorInput').value = '';
    });

    // Render Wardrobe Items
    const viewWardrobeButton = document.querySelector('.button.button-default-outline'); // Adjust the selector if necessary

    // Event listener for the "View My Wardrobe" button
    viewWardrobeButton.addEventListener('click', () => {
        renderWardrobeItems(); // Call the function to render items
    });

    // Function to render wardrobe items
    function renderWardrobeItems() {
        // wardrobeGrid.innerHTML = ''; // Clear previous items (removed)

        if (wardrobeItems.length === 0) {
            wardrobeGrid.innerHTML = 
                <div class="empty-state">
                    <i class="fas fa-hanger"></i>
                    <p>Your wardrobe is empty. Start adding items!</p>
                </div>
            ;
            return;
        }

        wardrobeItems.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.classList.add('wardrobe-item');
            itemElement.innerHTML = `
                <div class="item-image-container">
                    <img src="${item.imageUrl}" alt="${item.itemName}" />
                    <div class="item-overlay">
                        <button class="delete-btn" onclick="deleteItem(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="wardrobe-item-details">
                    <h3>${item.itemName}</h3>
                    <p>Category: ${item.category}</p>
                    <p>Color: ${item.color}</p>
                </div>
            `;
            wardrobeGrid.appendChild(itemElement);
        });
    }

    // Delete Item Function
    window.deleteItem = function(id) {
        // Confirmation dialog
        const confirmDelete = confirm('Are you sure you want to remove this item from your wardrobe?');
        
        if (confirmDelete) {
            // Filter out the item with the matching id
            wardrobeItems = wardrobeItems.filter(item => item.id !== id);
            
            // Update localStorage
            localStorage.setItem('wardrobeItems', JSON.stringify(wardrobeItems));
            
            // Re-render wardrobe
            renderWardrobeItems();
        }
    }

    // Initial render
    renderWardrobeItems();
});
