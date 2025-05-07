// Toggle mobile menu
document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("menuToggle");
    const nav = document.getElementById("navLinks");
  
    toggle.addEventListener("click", () => {
      nav.classList.toggle("active");
    });
  
    // Optional: close menu when any link is clicked
    document.querySelectorAll("#navLinks a").forEach(link => {
      link.addEventListener("click", () => {
        nav.classList.remove("active");
      });
    });
  });


  document.addEventListener("DOMContentLoaded", () => {
    
    const closeBtn = document.getElementById("closeBtn");
    const nav = document.getElementById("navLinks");
  
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        nav.classList.remove("active");
      });
    }
  });
    
  