"""Implementation of NovoGrad optimizer."""

import typing as tp

import torch
from torch.optim import Optimizer
from torch.optim.optimizer import ParamsT


class Novograd(Optimizer):
    """Novograd optimization algorithm.

    It has been proposed in "Stochastic Gradient Methods with Layer-wise
    Adaptive Moments for Training of Deep Networks"
    (https://arxiv.org/abs/1905.11286)

    Taken from https://github.com/jettify/pytorch-optimizer/blob/master/torch_optimizer/novograd.py
    """

    def __init__(
        self,
        params: ParamsT,
        lr: float = 1e-3,
        betas: tuple[float, float] = (0.95, 0.98),
        eps: float = 1e-8,
        weight_decay: float = 0,
        *,
        grad_averaging: bool = False,
        amsgrad: bool = False,
    ) -> None:
        """Initialize Novograd optimizer.

        Args:
            params: Iterable of parameters to optimize or dicts defining
                parameter groups
            lr: Learning rate
            betas: Coefficients used for computing running averages of gradient
                and its square
            eps: Term added to the denominator to improve numerical stability
            weight_decay: Weight decay (L2 penalty)
            grad_averaging: Whether to use grad averaging
            amsgrad: Whether to use the AMSGrad variant of this algorithm
        """
        self._check_args(lr, betas, eps, weight_decay)
        super().__init__(
            params,
            defaults={
                "lr": lr,
                "betas": betas,
                "eps": eps,
                "weight_decay": weight_decay,
                "grad_averaging": grad_averaging,
                "amsgrad": amsgrad,
            },
        )

    def __setstate__(self, state: dict[str, tp.Any]) -> None:
        super().__setstate__(state)
        for group in self.param_groups:
            group.setdefault("amsgrad", False)

    @staticmethod
    def _check_args(
        lr: float,
        betas: tuple[float, float],
        eps: float,
        weight_decay: float,
    ) -> None:
        if lr < 0.0:
            msg = f"Invalid learning rate: {lr}"
            raise ValueError(msg)
        if eps < 0.0:
            msg = f"Invalid epsilon value: {eps}"
            raise ValueError(msg)
        if not (0.0 <= betas[0] < 1.0 and 0.0 <= betas[1] < 1.0):
            msg = (
                f"Invalid beta parameters at index 0: {betas[0]} "
                f"and at index 1: {betas[1]}"
            )
            raise ValueError(msg)
        if weight_decay < 0:
            msg = f"Invalid weight_decay value: {weight_decay}"
            raise ValueError(msg)

    def step(  # noqa: PLR0912, C901
        self,
        closure: tp.Callable[[], float] | None = None,
    ) -> float:
        """Perform a single optimization step.

        Arguments:
            closure: A closure that reevaluates the model and returns the loss

        Raises:
            RuntimeError: If the optimizer does not support sparse gradients

        Returns:
            Loss value
        """
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    msg = (
                        "NovoGrad does not support sparse gradients, "
                        "please consider SparseAdam instead"
                    )
                    raise RuntimeError(msg)

                # State initialization
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0

                    # Exponential moving average of gradient values
                    state["exp_avg"] = torch.zeros_like(
                        p.data,
                        memory_format=torch.preserve_format,
                    )

                    # Exponential moving average of squared gradient values
                    state["exp_avg_sq"] = torch.zeros(
                        [],
                        device=state["exp_avg"].device,
                    )

                    if group["amsgrad"]:
                        # Maintains max of all exp. moving avg. of sq.
                        # grad. values
                        state["max_exp_avg_sq"] = torch.zeros(
                            [],
                            device=state["exp_avg"].device,
                        )

                exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
                if group["amsgrad"]:
                    max_exp_avg_sq = state["max_exp_avg_sq"]

                state["step"] += 1

                beta1, beta2 = group["betas"]
                norm = torch.sum(torch.pow(grad, 2))
                if exp_avg_sq == 0:
                    exp_avg_sq.copy_(norm)
                else:
                    exp_avg_sq.mul_(beta2).add_(norm, alpha=1 - beta2)

                if group["amsgrad"]:
                    # Maintains the maximum of all 2nd moment running avg.
                    # till now
                    torch.max(max_exp_avg_sq, exp_avg_sq, out=max_exp_avg_sq)
                    # Use the max. for normalizing running avg. of gradient
                    denom = max_exp_avg_sq.sqrt().add_(group["eps"])
                else:
                    denom = exp_avg_sq.sqrt().add_(group["eps"])

                grad.div_(denom)
                if group["weight_decay"] != 0:
                    grad.add_(p.data, alpha=group["weight_decay"])
                if group["grad_averaging"]:
                    grad.mul_(1 - beta1)
                exp_avg.mul_(beta1).add_(grad)

                p.data.add_(exp_avg, alpha=-group["lr"])

        return loss
