// ---------- Nav ----------- 
function openNav() {
    document.getElementById("mySidenav").style.width = "191px";

    // add close
    const node = document.createElement("A");                 
    const textnode = document.createTextNode("x");         
    node.appendChild(textnode); 
    node.href = "javascript:void(0)";
    node.className = "closebtn text-decoration-none";
    node.onclick = function closeNav() {
        document.getElementById("mySidenav").style.width = "0";
        document.querySelector(".closebtn").remove();
    }               
    document.getElementById("mySidenav").appendChild(node);

}
// ---------- /Nav ----------- 


// ---------- Create PG ----------
const reloadFunc = () => {
  location.reload();
}
// ---------- /Create PG ----------

// let upload = document.getElementById("res-pg-input")

// upload.onclick = function() {

// }

// ---------- info icon ----------
// Get the modal
let modal = document.getElementById("myModal");

// Get the button that opens the modal
let btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
let span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
// ---------- info icon ----------