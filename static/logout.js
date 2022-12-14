document.getElementById('logout').onclick = function () {
    firebase.auth().signOut();
    window.location.replace('/home')
  };