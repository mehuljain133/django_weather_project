  // Get the checkbox and the body
  var checkbox = document.querySelector('#toggle');
  var body = document.querySelector('body');

  // Attach the event listener
  checkbox.addEventListener('change', function() {
    // If the checkbox is checked, add the dark-mode class, otherwise remove it
    if(this.checked) {
      body.classList.add('darkmode');
    } else {
      body.classList.remove('darkmode');
    }
  });

