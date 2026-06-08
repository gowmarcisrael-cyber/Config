function localise() {
    const btn = document.getElementById('locate-btn');
    
    if (!navigator.geolocation) {
        alert('Géolocalisation non supportée par votre navigateur.');
        return;
    }

    btn.textContent = '⏳ Localisation...';
    btn.disabled = true;

    navigator.geolocation.getCurrentPosition(
        function(position) {
            document.querySelector('input[name="longitude"]').value = position.coords.longitude;
            document.querySelector('input[name="latitude"]').value = position.coords.latitude;
            document.querySelector('form').submit();
        },
        function(error) {
            btn.textContent = '📍 Me localiser';
            btn.disabled = false;
            alert('Impossible de vous localiser. Vérifiez les permissions.');
        }
    );
}
