const slider = document.querySelector(".slider");
const slides = document.querySelectorAll(".slide");
const prevBtn = document.querySelector(".prev");
const nextBtn = document.querySelector(".next");
const sliderTitle = document.getElementById("slider-title");

let slideIndex = 0;
slides[slideIndex].classList.add('active');
sliderTitle.innerText = slideIndex === 0 ? "Partitura Com Tom Mudado" : "Partitura Original";

prevBtn.addEventListener('click', () => changeSlide(-1));
nextBtn.addEventListener('click', () => changeSlide(1));

function changeSlide(direction) {
    slides[slideIndex].classList.remove('active');
    slideIndex = (slideIndex + direction + slides.length) % slides.length;
    slides[slideIndex].classList.add('active');
    slider.style.transform = `translate(-${slideIndex * 100}%)`;
    
    // Alterar o título de acordo com o slide atual
    sliderTitle.innerText = slideIndex === 0 ? "Partitura Com Tom Mudado" : "Partitura Original";
}