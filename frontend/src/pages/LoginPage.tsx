import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(72),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginFormValues) {
    setError(null);
    try {
      await login(values.email, values.password);
      const from = (location.state as { from?: Location })?.from?.pathname ?? "/";
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    }
  }

  return (
    <form className="form-card" onSubmit={handleSubmit(onSubmit)}>
      <h2>Log in</h2>
      <label>
        Email
        <input type="email" autoComplete="email" {...register("email")} />
        {errors.email ? <span className="field-error">{errors.email.message}</span> : null}
      </label>
      <label>
        Password
        <input type="password" autoComplete="current-password" {...register("password")} />
        {errors.password ? <span className="field-error">{errors.password.message}</span> : null}
      </label>
      {error ? <p className="form-error">{error}</p> : null}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Logging in..." : "Log in"}
      </button>
      <p className="form-note">
        No account yet? <Link to="/register">Create one</Link>
      </p>
    </form>
  );
}
