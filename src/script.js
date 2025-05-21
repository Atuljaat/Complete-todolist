let input = document.querySelector("#todobox")
let addBtn = document.querySelector('#addTodo')
let displayTodo = document.querySelector('#displayTodo')
let removeBtn = document.querySelectorAll('.removeBtn')
let updateBtn = document.querySelector('.updateBtn')
// let token = String(localStorage.getItem('token')) || null


addBtn.addEventListener('click', (e) => {
    e.preventDefault()
    let text = input.value
    if (text != null && text != "" ){
        addTodo(text)
        input.value = "";
    } else {
        alert("type something")
    }
})

async function addTodo (todo) {
    try {
        let res =  await fetch('http://127.0.0.1:5000/todo'
            , {
                method : "POST",
                headers: {
                    "Authorization":localStorage.getItem("token"),
                    "Content-Type": "application/json"
                },
                body : JSON.stringify({todo:todo})
            }
        )
        let data = await res.text()
        data = (JSON.parse(data)).todo
        console.log(data)
        if (data){
            createTodoElement(displayTodo,data[0])
        } 
        return data
    } catch (error) {
        console.log(error)
    }
}

function getTodos (){
    return fetch('http://127.0.0.1:5000/all',
        {
                method : "POST",
                headers: {
                    "Authorization":localStorage.getItem("token"),
                    "Content-Type": "application/json"
                },
            }
        )
    .then(res => res.json())
    .catch(error => console.log(error))
}

async function showTodos () {
    let allTodos = await getTodos();
    let i = 0;
    while (i < allTodos.length){
        createTodoElement(displayTodo,allTodos[i])
        i++
    }
}

function createTodoElement (parent,{id,todo,createdAt}) {
    let container = document.createElement('div')
    let mytodo = todoStructure(id,todo,createdAt)
    container.innerHTML = mytodo
    parent.appendChild(container)
}

function todoStructure (id,todo,createdAt) {
    return `
        <div
    id="${id}" 
    class="p-6 my-4 mx-10 bg-gradient-to-r from-blue-300 to-blue-400 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300"
  >
    <div class="flex flex-wrap justify-between items-center">
      <p class="  text-gray-900 text-lg font-medium tracking-wide">${String(todo)}</p>
      <div class="flex gap-3 mt-2 sm:mt-0">
        <button
            onclick="removeTodo(${id})"
          class="removeBtn bg-gray-900 text-white text-sm px-4 py-2 rounded-xl font-semibold transition-all duration-300 ease-in-out hover:scale-110 hover:bg-red-600 hover:shadow-md"
        >
          🗑 Remove
        </button>
        <button
          class="updateBtn bg-gray-900 text-white text-sm px-4 py-2 rounded-xl font-semibold transition-all duration-300 ease-in-out hover:scale-110 hover:bg-green-600 hover:shadow-md"
        onclick="updateTodo(${id})"
          >
          ✏️ Update
        </button>
      </div>
    </div>
    <p class="text-sm text-gray-700 mt-1 italic">Created at: ${createdAt}</p>
  </div>
    `
}

async function removeTodo (id) {
    try {
        let res = await fetch('http://127.0.0.1:5000/delete',
            {
                method:"POST",  
                headers : {
                    "Authorization":localStorage.getItem("token"),
                    "Content-Type":"application/json"
                },
                body : JSON.stringify({id:id})
            }   
        )
        if (res.ok){
            let element = document.getElementById(id)
            element.remove()
        }
    } catch (error){
        console.log(error)
    }
}

async function updateTodo (id) {
    let newTodo = prompt("Enter the updated value of todo : ")
    if (newTodo != null && newTodo != ""){
        let res = await fetch('http://127.0.0.1:5000/update', {
            method:"POST",
            headers : {
                "Authorization":localStorage.getItem("token"),
                "Content-Type":"application/json"
            },
            body : JSON.stringify({id:id,todo:newTodo})
        })
        if (res.ok){
            let textElement = document.getElementById(id).firstElementChild.firstElementChild
            textElement.innerText = newTodo
        }
    }
}

async function checkToken () {
    let token = String(localStorage.getItem('token'))
    if (!token){
        window.location.href = "login.html"
    } 
    let tokenStatus = await verifyToken(token)
    if (!tokenStatus){
        localStorage.removeItem('token')
        window.location.href = "login.html"
    }
}

async function verifyToken (token) {
    let response = await fetch('http://127.0.0.1:5000/protected',{
        method:'post',
        headers:{
            "Authorization" : String(token),
            "Content-Type":"application/json"
        }
    })

    if (response.ok){
        return true
    } else {
        return false
    }
}

document.addEventListener('DOMContentLoaded',(e)=>{
    checkToken()
    showTodos()
})

// removeBtn.addEventListener('click',(e)=>{
//     e.preventDefault()
//     console.log(e.target)
// })