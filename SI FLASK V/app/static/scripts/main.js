/*Movie Page*/
const see_more_button = document.querySelector('.see_more');
const text = document.querySelector('.text')

see_more_button.addEventListener('click', (e) =>{
    text.classList.toggle('show-more');
    if(see_more_button.innerText === 'See more'){
        see_more_button.innerText = 'See Less';
    }else{
        see_more_button.innerText = 'See more';
    }
})
