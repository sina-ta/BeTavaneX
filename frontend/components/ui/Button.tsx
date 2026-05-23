type ButtonProps = {

  children: React.ReactNode;

  type?: "button" | "submit";

};

export default function Button({
  children,
  type = "button",
}: ButtonProps) {

  return (

    <button
      type={type}
      className="button-primary"
    >

      {children}

    </button>

  );
}