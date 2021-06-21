const form = $('#plan_form')
const new_form = $('#singup-form')
const new_list = []


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

async function get_list(){
   const options = {headers: {'Content-Type': 'application/x-www-form-urlencoded'}}
    new_list.forEach(meal => {
        const resp = axios.post('/api/shopping', [`ingredientList=${meal.ingredientList}`, `servings=${meal.servings}`],options )
    console.log(resp)
    handle_list(resp.data)
})
}
function handle_list(resp){
    $('#plan_info').append(resp)
}

function handle_response(resp){
data = JSON.parse(resp)

console.log(Object.entries(data.week))
Object.entries(data.week).forEach(([dayName, { meals }]) => {
    $('#plan_info').append(`<h1>${dayName}</h1>`)
    
    meals.forEach(meal => {console.log(meal)
        new_list.push({ingredientList:meal.title, servings:meal.servings})
        console.log(new_list)
        Object.entries(meal).forEach(([title, value]) => {
            console.log(title, value)
            $('#plan_info').append(`<p>${title}: ${value}</p>`)})
})

});
console.log(new_list)
get_list()
}
form.on("submit", handle_form);

