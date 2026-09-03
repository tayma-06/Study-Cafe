function Login() {
  return (
    <main>
      <h1>Study Café</h1>
      <h2>Login</h2>

      <form>
        <div>
          <label>Email</label>
          <br />
          <input type="email" />
        </div>

        <br />

        <div>
          <label>Password</label>
          <br />
          <input type="password" />
        </div>

        <br />

        <button type="submit">Login</button>
      </form>

      <p>
        Don't have an account? <a href="#">Register</a>
      </p>
    </main>
  );
}

export default Login;