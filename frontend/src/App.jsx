import React from "react";

import { useAuth, useUser } from "@clerk/clerk-react";

function App() {
  const { isSignedIn, user } = useUser();
  const { getToken } = useAuth(); // ✅ Use useAuth() to get the token

  async function fetchToken() {
    try {
      if (!isSignedIn) {
        console.log("User not signed in!");
        return;
      }

      const token = await getToken(); // ✅ Correct way to get the token
      console.log("JWT Token:", token);
    } catch (error) {
      console.error("Error fetching token:", error);
    }
  }

  return (
    <div>
      {isSignedIn ? (
        <>
          <h1>Welcome, {user?.fullName}</h1>
          <button onClick={fetchToken}>Get Token</button>
        </>
      ) : (
        <h1>Please log in</h1>
      )}
    </div>
  );
}

export default App;
