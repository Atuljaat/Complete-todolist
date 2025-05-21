let loginBtn = document.getElementById('loginBtn')
let email = document.getElementById('email')
let password = document.getElementById('pass')
let error = document.getElementById('errors')
let signupBtn = document.getElementById('signupBtn')
let username = document.getElementById('name')

const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

signupBtn.addEventListener('click',(e)=>{
    e.preventDefault()
    let emailInfo = String(email.value)
    let errors = []
    if (!emailInfo || !(emailRegex.test(emailInfo)) ){
        error.innerText = "enter a valid email"
        errors.push("email is not valid")
    }
    let nameInfo = String(username.value)
    if (3 >= nameInfo.length){
        error.innerText = "name should be greater than 3 characters"
        errors.push("name is not valid")
    }
    let passInfo = String(password.value)
    if (!passInfo){
        error.innerText = "enter a valid password"
        errors.push("password is not valid")
    }
    if (passInfo.length < 8){
        error.innerText = "password must be greater than 8 digits"
        errors.push("password is not greater than 8 digits")
    }
    if (errors.length > 0 ){
        error.innerText = errors.join("\n")
    }else {
        signup(nameInfo,emailInfo,passInfo)
    }
})

async function signup (username,email,password){
    let response = await fetch('http://127.0.0.1:5000/signup',{
        method:'post',
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({name:username,email:email,password:password})
    })
    let data = await response.text()
    console.log(data)
    if (response.ok){
        window.location.href = "login.html"
    }
}