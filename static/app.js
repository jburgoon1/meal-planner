const form = $('#plan_form')
const new_form = $('#singup-form')
const list_form = $('#list_form')
const plan_text = $('#plan_info')
const new_list = []
//append the new plan from the session to the page for the user to see
if (localStorage.getItem("plan")) {
    plan_text.html(localStorage.getItem("plan"))
}
//grab the info from the new plan form and send it to the api in flask
async function handle_form(evt){
    evt.preventDefault();
    const data = new FormData(form.get(0))
    console.log(data.get("timeFrame"))
    console.log(data.get("targetCalories"))
    console.log(data.get("diet"))
    const duration = data.get("timeFrame")
    const calories = data.get("targetCalories")
    const diet = data.get("diet")
    const resp = await axios.post('/api/newplan', {timeFrame: duration, calories: calories, diet:diet});
    
    handle_response(resp.data.new_plan);
}


//handle the response from the flask to append the newly created plan to the page
function handle_response(resp){
data = JSON.parse(resp)
plan_text.html('')
localStorage.removeItem('plan')
console.log(Object.entries(data.week))
Object.entries(data.week).forEach(([dayName, { meals }]) => {
   
    $('#plan_info').append(`<div class = "container"><div class = "row"<div class = "col"><div class="card" style="width: 18rem;">
    <div class="card-body" id = "plan_title">
    <h1>${dayName}</h1>
    </div>
    
  </div></div></div></div>`)
    
    meals.forEach(meal => {console.log(meal)
        new_list.push({ingredientList:meal.title, servings:meal.servings})
        console.log(new_list)
        
        $('#plan_info').append(`<div class = "container"><div class = "row"<div class = "col"><div class="card" style="width: 18rem;"><ul class="list-group list-group-flush" id = "plan_list">
            <li class="list-group-item">Title: ${meal.title}</li>
            <li class="list-group-item">Servings: ${meal.servings}</li>
            <li class="list-group-item">Ready In: ${meal.readyInMinutes}</li>
            <li class="list-group-item"><a href = "${meal.sourceUrl}">Recipe Instructions</a></li>
           
            </ul></div></div></div></div> `)})
//         Object.entries(meal).forEach(([title, value]) => {
//             console.log(title, value)
            
// })

});
console.log(new_list)
const plan = plan_text.html()
localStorage.setItem('plan', plan)

}
form.on("submit", handle_form);

