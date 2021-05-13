function processInPython() {
    let rec;
    if (!("webkitSpeechRecognition" in window)) {
        alert("Hay un error en el microfono");
    } else {
        rec = new webkitSpeechRecognition();
        rec.lang = "es-ES";
        rec.continuous = true;
        rec.interim = true;
        rec.addEventListener("result", iniciar);
    }

    function iniciar(event) {
        for (let i = event.resultIndex; i < event.results.length; i++) {
            index = event.results[i][0].transcript;
            alert(index);
            fetch(`/getdataBio/${index}`,{
                method: 'POST'
            })
                .then(function(response){
                    return response.text();
                }).then(function(text) {;
                    document.getElementById("p").innerHTML = text
                });

        }

    }
    rec.start();
}