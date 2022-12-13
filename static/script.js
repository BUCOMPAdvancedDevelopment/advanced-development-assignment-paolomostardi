/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// [START gae_python38_log]
'use strict';



function createList(){
    // create the ordered list
    const ol = document.createElement("ol");
    // iterate over the data and create list items for each item
    fetch("https://adassigment.ew.r.appspot.com/getListOfGames")
     .then(response => response.text())
  .then(data => {
    data = data.slice(1, -1);
    data = data.split("), (");
    data = data.map(item => {
      item = item.slice(1, -1);
      item = item.split(", ");
      const id = parseInt(item[0]);
      const name = item[1].slice(1, -1);
      const description = item[2].slice(1, -1);
      return {
        id,name,description};
    });
    data.forEach((item) => {
      const li = document.createElement("li");
      li.innerText = `${item.name}: ${item.description}`;
      const btn = document.createElement("button");
      btn.innerText = "add";
      btn.addEventListener("click", () => {
        fetch("https://adassigment.ew.r.appspot.com/addGame")
      });
      li.appendChild(btn);
      ol.appendChild(li);
    });
    // get the paragraph element where you want to insert the ordered list
    const p = document.getElementById("paragraph")
    // insert the ordered list into the paragraph
    p.innerHTML = ol.outerHTML;
  });
}


window.addEventListener('load', function () {
  document.getElementById('sign-out').onclick = function () {
    firebase.auth().signOut();
  };

  document.getElementById('show-games').onclick = createList()





  // FirebaseUI config.
  var uiConfig = {
    signInSuccessUrl: '/home',
    signInOptions: [
      // Comment out any lines corresponding to providers you did not check in
      // the Firebase console.
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID,
      //firebase.auth.FacebookAuthProvider.PROVIDER_ID,
      //firebase.auth.TwitterAuthProvider.PROVIDER_ID,
      //firebase.auth.GithubAuthProvider.PROVIDER_ID,
      //firebase.auth.PhoneAuthProvider.PROVIDER_ID

    ],
    // Terms of service url.
    tosUrl: '<your-tos-url>'
  };

  firebase.auth().onAuthStateChanged(function (user) {
    if (user) {
      // User is signed in, so display the "sign out" button and login info.
      document.getElementById('sign-out').hidden = false;
      document.getElementById('login-info').hidden = false;
      document.getElementById('show-games').hidden = false;
      console.log(`Signed in as ${user.displayName} (${user.email})`);
      user.getIdToken().then(function (token) {
        // Add the token to the browser's cookies. The server will then be
        // able to verify the token against the API.
        // SECURITY NOTE: As cookies can easily be modified, only put the
        // token (which is verified server-side) in a cookie; do not add other
        // user information.
        document.cookie = "token=" + token;
      });
    } else {
      // User is signed out.
      // Initialize the FirebaseUI Widget using Firebase.
      var ui = new firebaseui.auth.AuthUI(firebase.auth());
      // Show the Firebase login button.
      ui.start('#firebaseui-auth-container', uiConfig);
      // Update the login state indicators.
      document.getElementById('sign-out').hidden = true;
      document.getElementById('login-info').hidden = true;
      document.getElementById('show-games').hidden = true;
      // Clear the token cookie.
      document.cookie = "token=";
    }
  }, function (error) {
    console.log(error);
    alert('Unable to log in: ' + error)
  });
})