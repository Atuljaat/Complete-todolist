let loginBtn = document.getElementById('loginBtn')
let email = document.getElementById('email')
let password = document.getElementById('pass')
let error = document.getElementById('errors')
let signupBtn = document.getElementById('signupBtn')

const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;


loginBtn.addEventListener('click',(e)=>{
    e.preventDefault()
    let emailInfo = email.value
    let pass = password.value
    if (!emailInfo || !(emailRegex.test(emailInfo)) ){
        error.innerText = "enter a valid email"
    }
    if (pass == "" && pass == null ){
        error.innerText = 'enter a valid password'
    }
    if (email && pass) {
        login(emailInfo,pass)
    }
})

async function login (email,pass){
    let res =  await fetch('http://127.0.0.1:5000/login',{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({email:String(email),password:String(pass)})
    })
    if (res.ok){
        let txt = await res.json()
        localStorage.setItem('token',String(txt.token))
        setTimeout(()=>{
            window.location.href = "index.html"
        } , 500 )
    }
}
