// for scrolling messages
function scrollToBottom() {
    var div = document.getElementById("upperid");
    div.scrollTop = div.scrollHeight;
}
scrollToBottom()
document.getElementById("userinputform").addEventListener("submit", function (event) {
    event.preventDefault();
    formsubmitted();
});

// sending request to python server
const formsubmitted = async () => {
    let userinput = document.getElementById('userinput').value
    let sendbtn = document.getElementById('sendbtn')
    let userinputarea = document.getElementById('userinput')
    let upperdiv = document.getElementById('upperid')   

    upperdiv.innerHTML = upperdiv.innerHTML + `<div class="message">
        <div class="usermessagediv">
                <div class="usermessage">
                    ${userinput}
                </div>
        </div>
    </div>`
    sendbtn.disabled = true
    userinputarea.disabled = true
    scrollToBottom()
    document.getElementById('userinput').value = ""
    document.getElementById('userinput').placeholder = "Wait . . ."

    const response = await fetch("http://127.0.0.1:5000/data", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: userinput })


    });
    let json = await response.json();

    document.getElementById('userinput').placeholder = "Your message..."


    if (json.response) {
        let message = json.message
        message = message.toString()

        upperdiv.innerHTML = upperdiv.innerHTML + `<div class="message">
        <div class="appmessagediv">
            <div class="appmessage" id="temp">
                
            </div>
        </div>
    </div>`
        let temp = document.getElementById('temp')
        let index = 0
        function displayNextLetter() {
            scrollToBottom()
            if (index < message.length) {
                temp.innerHTML = temp.innerHTML + message[index];
                index++;
                setTimeout(displayNextLetter, 30);
            } else {
                temp.removeAttribute('id')
                sendbtn.disabled = false
                userinputarea.disabled = false
            }
        }
        displayNextLetter()
        scrollToBottom()

    }
    else {
        let message = json.message
        upperdiv.innerHTML = upperdiv.innerHTML +
            `<div class="message">
        <div class="appmessagediv">
            <div class="appmessage"  style="border: 1px solid red;">
              ${message}

            </div>
        </div>
    </div>`
        sendbtn.disabled = false
        userinputarea.disabled = false
    }

    scrollToBottom()


} 
