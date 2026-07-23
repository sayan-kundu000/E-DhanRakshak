import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { Input } from '../components/UI/FormComponents';
import { Button } from '../components/UI/UI';
import { ROUTES } from '../constants';

export const Login = () => {
  const { login } = useAuth();
  const { success, error } = useNotification();
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || ROUTES.DASHBOARD;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data) => {
    setSubmitting(true);
    const result = await login(data.email, data.password);
    setSubmitting(false);

    if (result.success) {
      success('Logged in successfully!');
      navigate(from, { replace: true });
    } else {
      error(result.error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <Input
        label="Email Address"
        type="email"
        error={errors.email?.message}
        placeholder="e.g. officer@erakshak.gov"
        {...register('email', {
          required: 'Email address is required.',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: 'Invalid email address formatting.',
          },
        })}
      />

      <Input
        label="Password"
        type="password"
        error={errors.password?.message}
        placeholder="••••••••"
        {...register('password', {
          required: 'Password is required.',
          minLength: {
            value: 6,
            message: 'Password must be at least 6 characters long.',
          },
        })}
      />

      <Button type="submit" loading={submitting} className="w-full">
        Sign In
      </Button>

      <div className="text-center text-sm text-slate-500 dark:text-slate-400 mt-4 border-t border-slate-100 dark:border-slate-800 pt-4">
        <span>Need a citizen account? </span>
        <Link to={ROUTES.REGISTER} className="text-brand-600 dark:text-brand-400 font-semibold hover:underline">
          Register here
        </Link>
      </div>
    </form>
  );
};
export default Login;
