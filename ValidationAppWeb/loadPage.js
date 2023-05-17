
window.onload = function() {
    // Obtener los elementos HTML
    const uploadForm = document.getElementById("uploadForm");
    const csvFile = document.getElementById("csvFile");
    const csvFileName = document.getElementById("csvFileName");
    const csvFileContent = document.getElementById("csvFileContent");

    // Manejar el envío del formulario
    uploadForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const file = csvFile.files[0];
        const reader = new FileReader();
        reader.onload = function(event) {
            // Mostrar el nombre del archivo
            csvFileName.textContent = `Archivo seleccionado: ${file.name}`;

            // Mostrar el contenido del archivo
            const contents = event.target.result;
            csvFileContent.textContent = `Contenido del archivo:\n${contents}`;
        };
        reader.readAsText(file);
    });
};