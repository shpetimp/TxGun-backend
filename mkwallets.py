#!/usr/bin/python3

# pip install ecdsa
# pip install pysha3

from ecdsa import SigningKey, SECP256k1
import sha3


for i in range(2, 21):
    keccak = sha3.keccak_256()

    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key().to_string()

    keccak.update(pub)
    address = keccak.hexdigest()[24:]
    print()
    print("# AIRDROP KEY #%s"%i)
    print("export SHIPYARD_AIRDROP_KEY_%s=%s"%(i, priv.to_string().hex()))
    print("export SHIPYARD_AIRDROP_ADDR_%s=0x%s"%(i, address))
    print()
