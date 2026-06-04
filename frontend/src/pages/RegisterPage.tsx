import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

const registerSchema = z
  .object({
    email: z.string().email(),
    password: z.string().min(8).max(72),
    confirmPassword: z.string().min(8).max(72),
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: "Passwords must match",
    path: ["confirmPassword"],
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({ resolver: zodResolver(registerSchema) });

  async function onSubmit(values: RegisterFormValues) {
    setError(null);
    try {
      await registerUser({ email: values.email, password: values.password });
      navigate("/onboarding", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    }
  }

  return (
    <form className="form-card" onSubmit={handleSubmit(onSubmit)}>
      <h2>Create account</h2>
      <label>
        Email
        <input type="email" autoComplete="email" {...register("email")} />
        {errors.email ? <span className="field-error">{errors.email.message}</span> : null}
      </label>
      <label>
        Password
        <input type="password" autoComplete="new-password" {...register("password")} />
        {errors.password ? <span className="field-error">{errors.password.message}</span> : null}
      </label>
      <label>
        Confirm password
        <input type="password" autoComplete="new-password" {...register("confirmPassword")} />
        {errors.confirmPassword ? <span className="field-error">{errors.confirmPassword.message}</span> : null}
      </label>
      {error ? <p className="form-error">{error}</p> : null}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create account"}
      </button>
      <p className="form-note">
        Already registered? <Link to="/login">Log in</Link>
      </p>
    </form>
  );
}
