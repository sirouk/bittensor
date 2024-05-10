import asyncio
from functools import partial
import time

# import sys

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

import bittensor
from bittensor.commands import network
from bittensor.commands import metagraph
from bittensor.commands import register

# Attempting to get around nest_asyncio from bittensor.__init__.py
# if "nest_asyncio" in sys.modules:
#     asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())


# TODO app-wide error-handling

sub = bittensor.subtensor("test")
app = FastAPI(debug=True)
config = {"netuid": 0}


@app.get("/subnets/{sub_cmd}")
async def get_subnet(sub_cmd: str):
    routing_list = {
        "list": network.SubnetListCommand,
        "metagraph": metagraph.MetagraphCommand,
        "lock_cost": network.SubnetLockCostCommand,
        "create": network.RegisterSubnetworkCommand,
        "pow_register": register.PowRegisterCommand,
        "register": register.RegisterCommand,
        "hyperparameters": network.SubnetHyperparamsCommand,
    }
    start = time.time()
    try:
        command_class = routing_list[sub_cmd]
        if hasattr(command_class, "commander_run"):
            # Offload synchronous execution to the threadpool
            response_content = await asyncio.get_event_loop().run_in_executor(
                None, partial(command_class.commander_run, sub, config=config)
            )
            print(sub_cmd, time.time() - start)
            return JSONResponse(content=response_content)
        else:
            raise HTTPException(
                status_code=501, detail="Command implementation missing"
            )
    except Exception as e:
        raise
        # raise HTTPException(status_code=500, detail=str(e))
