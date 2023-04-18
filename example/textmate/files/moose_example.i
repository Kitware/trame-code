[Mesh]
  # Let's assign human friendly names to the blocks on the fly
  block_id = '1 2'
  block_name = 'fuel deflector'
  boundary_id = '4 5'
  boundary_name = 'bottom top'
  file = reactor.e
[]

[Variables]
  [diffused]
    order = FIRST
    family = LAGRANGE
    initial_condition = '0.5' # shortcut/convenience for setting constant initial condition
  []
  [convected]
    order = FIRST
    family = LAGRANGE
    initial_condition = '0.0' # shortcut/convenience for setting constant initial condition
  []
[]

[Kernels]
  # This Kernel consumes a real-gradient material property from the active material
  [convection]
    type = ExampleConvection
    variable = convected
  []
  [diff_convected]
    type = Diffusion
    variable = convected
  []
  [example_diff]
    # This Kernel uses "diffusivity" from the active material
    type = ExampleDiffusion
    variable = diffused
  []
  [time_deriv_diffused]
    type = TimeDerivative
    variable = diffused
  []
  [time_deriv_convected]
    type = TimeDerivative
    variable = convected
  []
[]

[BCs]
  [bottom_diffused]
    type = DirichletBC
    variable = diffused
    boundary = 'bottom'
    value = 0.0
  []
  [top_diffused]
    type = DirichletBC
    variable = diffused
    boundary = 'top'
    value = 5.0
  []
  [bottom_convected]
    type = DirichletBC
    variable = convected
    boundary = 'bottom'
    value = 0.0
  []
  [top_convected]
    type = NeumannBC
    variable = convected
    boundary = 'top'
    value = 1.0
  []
[]

[Materials]
  [example]
    # Approximate Parabolic Diffusivity
    type = ExampleMaterial
    block = 'fuel'
    diffusion_gradient = 'diffused'
    independent_vals = '0.0 0.25 0.5 0.75 1.0'
    dependent_vals = '0.01 0.005 0.001 0.005 0.01'
  []
  [example1]
    # Constant Diffusivity
    type = ExampleMaterial
    block = 'deflector'
    diffusion_gradient = 'diffused'
    independent_vals = '0.0 1.0'
    dependent_vals = '0.1 0.1'
  []
[]

[Executioner]
  type = Transient
  solve_type = PJFNK
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
  dt = 0.1
  num_steps = 10
[]

[Outputs]
  execute_on = 'timestep_end'
  exodus = true
[]
