function previewImages(input) {
    const preview = document.getElementById('preview');
    preview.innerHTML = '';
    if (input.files) {
        [...input.files].forEach(file => {
            const reader = new FileReader();
            reader.onload = e => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'h-20 w-28 object-cover rounded-lg border border-gray-200';
                preview.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    }
}