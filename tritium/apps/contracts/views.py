from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Contract, get_etherscan_abi
from tritium.apps.networks.models import MAIN_NETWORK
import json

class GetABI(APIView):
    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Response({'error': 'You are not logged in'}, status=401)

        address = self.request.query_params.get("address", None)
        network = self.request.query_params.get("network", "mainnet")

        if not address:
            return Response({
                "error": "You must specify a contract address"
            })
        if network != "mainnet":
            return Response({
                "error": "You must specify a network"
            })

        # Try to lookup contract by address, if found return the ABI
        try:
            contract = Contract.objects.get(address=address)
            return Response({
                "abi": contract.abi_object(),
                "name": contract.nickname,
            })
        except Contract.DoesNotExist:
            pass

        # Try to look up the ABI with etherscan; if found, create the contract
        # and return the ABI
        try:
            abi = get_etherscan_abi(address)
            contract = Contract.objects.create(
                address=address,
                abi=json.dumps(abi),
                network=MAIN_NETWORK()
            )
            return Response({
                "abi": contract.abi_object(),
                "name": contract.nickname,
            })
        except Exception as e:
            print(e)
            return Response({
                "error": "Unable to look up abi"
            })
        # Else return "couldn't find the ABI" error