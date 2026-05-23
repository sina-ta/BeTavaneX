type InputProps = {

  label: string;

  type?: string;

  name: string;

  value: string | number;

  onChange: (
    e: React.ChangeEvent<HTMLInputElement>
  ) => void;

  placeholder?: string;

};

export default function Input({
  label,
  type = "text",
  name,
  value,
  onChange,
  placeholder,
}: InputProps) {

  return (

    <div className="space-y-2">

      <label className="input-label">

        {label}

      </label>

      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="input-base"
      />

    </div>

  );
}